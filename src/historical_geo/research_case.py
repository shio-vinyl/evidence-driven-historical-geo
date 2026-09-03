"""Case-level entry points for the auditable research loop."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from rasterio.features import rasterize
from shapely.geometry import mapping, shape

from historical_geo import xtent
from historical_geo.adapter import load_case
from historical_geo.backends.xtent_backend import compile_xtent_solver_input
from historical_geo.compiler import compile_reconstruction_request
from historical_geo.diagnosis import build_diagnosis_documents
from historical_geo.pipeline import (
    _geometry_to_grid_crs,
    _read_feature_collection,
    reconstruct_solver_input,
    run_directory,
)
from historical_geo.research_contracts import (
    load_json,
    validate_research_bundle,
    validate_search_targets,
    validate_uncertainty_diagnosis,
)

RESEARCH_BUNDLE_FILE = "research-bundle.json"
RESEARCH_SCENARIOS_FILE = "research-scenarios.json"
_PER_SLICE_FIELDS = frozenset({"included_decision_ids", "excluded_decision_ids", "changed_decision_ids"})


def _slice_value(value: Any, slice_value: int | str, field: str) -> Any:
    if field in _PER_SLICE_FIELDS and isinstance(value, Mapping):
        return deepcopy(value.get(str(slice_value), []))
    return deepcopy(value)


def scenario_profile(case_dir: Path, slice_value: int | str, scenario: str) -> dict[str, Any]:
    """Flatten a checked-in scenario definition for a single temporal slice."""
    config = load_json(case_dir.resolve() / RESEARCH_SCENARIOS_FILE)
    profiles = config.get("scenarios", {})
    if scenario not in profiles:
        raise ValueError(f"unsupported research scenario: {scenario}")
    raw = profiles[scenario]
    if not isinstance(raw, Mapping):
        raise ValueError(f"research scenario {scenario} must be an object")
    profile = {key: _slice_value(value, slice_value, key) for key, value in raw.items()}
    profile.setdefault("name", scenario)
    return profile


def compile_case_request(
    case_dir: Path, slice_value: int | str, scenario: str = "reviewed-baseline"
) -> dict[str, Any]:
    """Compile one case without exposing XTENT-specific roles to the research layer."""
    case_dir = case_dir.resolve()
    case = load_case(case_dir)
    bundle = load_json(case_dir / RESEARCH_BUNDLE_FILE)
    validation = validate_research_bundle(bundle)
    validation.require_ok()
    profile = scenario_profile(case_dir, slice_value, scenario)
    return compile_reconstruction_request(bundle, slice_value, profile, case["grid"])


def reconstruct_research_case(
    case_dir: Path, slice_value: int | str, scenario: str = "reviewed-baseline"
) -> Path:
    """Compile epistemic state, cross the backend boundary, and run XTENT."""
    request = compile_case_request(case_dir, slice_value, scenario)
    solver_input = compile_xtent_solver_input(request)
    return reconstruct_solver_input(case_dir, solver_input)


def _diagnostic_config(case_dir: Path, slice_value: int | str) -> dict[str, Any]:
    raw = load_json(case_dir.resolve() / RESEARCH_SCENARIOS_FILE)
    baseline = raw.get("baseline")
    scenarios: dict[str, Any] = {}
    for name in raw.get("scenarios", {}):
        profile = scenario_profile(case_dir, slice_value, name)
        if name != baseline and not profile.get("changed_decision_ids"):
            continue
        scenarios[name] = profile
    return {"baseline": baseline, "scenarios": scenarios}


def _assignment_arrays(
    case_dir: Path, slice_value: int | str, scenario_names: list[str]
) -> dict[str, np.ndarray]:
    case_dir = case_dir.resolve()
    grid_config = load_case(case_dir)["grid"]
    analysis_grid = xtent.build_grid(
        tuple(grid_config["bbox"]), float(grid_config["resolution"]), str(grid_config["crs"])
    )
    surfaces: dict[str, list[dict[str, Any]]] = {}
    entities: set[str] = set()
    for scenario in scenario_names:
        run = reconstruct_research_case(case_dir, slice_value, scenario)
        features = _read_feature_collection(run / "boundary-hypotheses.geojson")
        surfaces[scenario] = features
        entities.update(str(feature["properties"]["entity"]) for feature in features)
    codes = {entity: index + 1 for index, entity in enumerate(sorted(entities))}
    arrays: dict[str, np.ndarray] = {}
    for scenario, features in surfaces.items():
        items = [
            (
                mapping(_geometry_to_grid_crs(shape(feature["geometry"]), analysis_grid.crs)),
                codes[str(feature["properties"]["entity"])],
            )
            for feature in features
        ]
        arrays[scenario] = rasterize(
            items,
            out_shape=analysis_grid.shape,
            transform=analysis_grid.transform,
            fill=0,
            dtype="int16",
        )
    return arrays


def run_research_loop(case_dir: Path, slice_value: int | str) -> tuple[Path, Path]:
    """Diagnose spatial sensitivity and write the next evidence-search agenda."""
    case_dir = case_dir.resolve()
    bundle = load_json(case_dir / RESEARCH_BUNDLE_FILE)
    validation = validate_research_bundle(bundle)
    validation.require_ok()
    config = _diagnostic_config(case_dir, slice_value)
    arrays = _assignment_arrays(case_dir, slice_value, list(config["scenarios"]))
    diagnosis, targets = build_diagnosis_documents(
        bundle["case_id"], config, {slice_value: arrays}, bundle["evidence_gaps"]
    )
    validate_uncertainty_diagnosis(diagnosis, bundle).require_ok()
    validate_search_targets(targets, bundle).require_ok()

    output = case_dir / "build" / "research-loop"
    output.mkdir(parents=True, exist_ok=True)
    diagnosis_path = output / f"uncertainty-diagnosis-{slice_value}.json"
    targets_path = output / f"search-targets-{slice_value}.json"
    for path, document in ((diagnosis_path, diagnosis), (targets_path, targets)):
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return diagnosis_path, targets_path


__all__ = [
    "compile_case_request",
    "reconstruct_research_case",
    "run_research_loop",
    "scenario_profile",
]
