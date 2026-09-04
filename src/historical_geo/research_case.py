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
    if case.get("reconstruction_ready") is False:
        raise ValueError("prospective case is not reconstruction-ready")
    bundle = load_json(case_dir / RESEARCH_BUNDLE_FILE)
    validation = validate_research_bundle(bundle)
    validation.require_ok()
    profile = scenario_profile(case_dir, slice_value, scenario)
    return _compile_profile(bundle, case["grid"], slice_value, profile)


def _compile_profile(
    bundle: Mapping[str, Any], grid: Mapping[str, Any], slice_value: int | str, profile: Mapping[str, Any]
) -> dict[str, Any]:
    """Compile an already flattened scenario profile.

    This deliberately remains private: public callers select a checked-in
    scenario by name, while the research loop may derive isolated diagnostic
    counterfactuals from that manifest.
    """
    return compile_reconstruction_request(bundle, slice_value, profile, grid)


def reconstruct_research_case(
    case_dir: Path, slice_value: int | str, scenario: str = "reviewed-baseline"
) -> Path:
    """Compile epistemic state, cross the backend boundary, and run XTENT."""
    request = compile_case_request(case_dir, slice_value, scenario)
    solver_input = compile_xtent_solver_input(request)
    return reconstruct_solver_input(case_dir, solver_input)


def _reconstruct_profile(
    case_dir: Path, bundle: Mapping[str, Any], grid: Mapping[str, Any], slice_value: int | str,
    profile: Mapping[str, Any],
) -> Path:
    request = _compile_profile(bundle, grid, slice_value, profile)
    return reconstruct_solver_input(case_dir, compile_xtent_solver_input(request))


def _isolated_evidence_profiles(
    case_dir: Path, slice_value: int | str, raw: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    """Expand each grouped evidence variant into single-decision interventions.

    A grouped ``inclusive`` or ``verified-only`` scenario is useful for a
    reconstruction comparison, but it cannot establish the marginal spatial
    effect of each of its decisions.  The loop therefore derives a separate
    profile for every changed evidence decision, relative to the same baseline.
    """
    baseline_name = raw.get("baseline")
    if not isinstance(baseline_name, str) or not baseline_name:
        raise ValueError("research scenarios must declare a baseline")
    baseline = scenario_profile(case_dir, slice_value, baseline_name)
    baseline_included = set(baseline.get("included_decision_ids", []))
    baseline_excluded = set(baseline.get("excluded_decision_ids", []))
    profiles: dict[str, dict[str, Any]] = {}

    for scenario_name, definition in raw.get("scenarios", {}).items():
        if not isinstance(definition, Mapping) or definition.get("axis") != "evidence":
            continue
        grouped = scenario_profile(case_dir, slice_value, scenario_name)
        changed = grouped.get("changed_decision_ids", [])
        if not isinstance(changed, list) or not all(isinstance(value, str) and value for value in changed):
            raise ValueError(f"evidence scenario {scenario_name!r} needs changed_decision_ids for isolation")
        # A scenario may legitimately coincide with the new baseline after a
        # reviewed round closes its former evidence gaps.  It supplies no
        # counterfactual for this slice and must not manufacture one.
        if not changed:
            continue
        grouped_included = set(grouped.get("included_decision_ids", []))
        grouped_excluded = set(grouped.get("excluded_decision_ids", []))

        for decision_id in changed:
            name = f"isolated-{decision_id}"
            if name in profiles:
                raise ValueError(f"decision {decision_id!r} appears in more than one evidence scenario")
            if decision_id in grouped_excluded and decision_id not in baseline_excluded:
                included = baseline_included - {decision_id}
                excluded = baseline_excluded | {decision_id}
            elif decision_id in grouped_included and decision_id not in baseline_included:
                included = baseline_included | {decision_id}
                excluded = baseline_excluded
            else:
                raise ValueError(
                    f"cannot derive isolated intervention for {decision_id!r} from evidence scenario "
                    f"{scenario_name!r}"
                )
            profiles[name] = {
                "name": name,
                "axis": "evidence",
                "description": f"Isolated counterfactual for {decision_id} from {scenario_name}.",
                "changed_decision_ids": [decision_id],
                "included_decision_ids": sorted(included),
                "excluded_decision_ids": sorted(excluded),
            }
    return profiles


def _diagnostic_config(case_dir: Path, slice_value: int | str) -> dict[str, Any]:
    raw = load_json(case_dir.resolve() / RESEARCH_SCENARIOS_FILE)
    baseline = raw.get("baseline")
    scenarios: dict[str, Any] = {}
    for name in raw.get("scenarios", {}):
        profile = scenario_profile(case_dir, slice_value, name)
        if name != baseline and (profile.get("axis") == "evidence" or not profile.get("changed_decision_ids")):
            continue
        scenarios[name] = profile
    scenarios.update(_isolated_evidence_profiles(case_dir, slice_value, raw))
    return {"baseline": baseline, "scenarios": scenarios}


def _assignment_arrays(
    case_dir: Path, slice_value: int | str, scenario_profiles: Mapping[str, Mapping[str, Any]]
) -> dict[str, np.ndarray]:
    case_dir = case_dir.resolve()
    case = load_case(case_dir)
    grid_config = case["grid"]
    bundle = load_json(case_dir / RESEARCH_BUNDLE_FILE)
    analysis_grid = xtent.build_grid(
        tuple(grid_config["bbox"]), float(grid_config["resolution"]), str(grid_config["crs"])
    )
    surfaces: dict[str, list[dict[str, Any]]] = {}
    entities: set[str] = set()
    for scenario, profile in scenario_profiles.items():
        run = _reconstruct_profile(case_dir, bundle, grid_config, slice_value, profile)
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
    arrays = _assignment_arrays(case_dir, slice_value, config["scenarios"])
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
