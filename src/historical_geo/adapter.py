"""Translate reviewed model decisions into bounded XTENT scenario inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from historical_geo.contracts import SOLVER_INPUT_VERSION, load_json, validate_lineage_bundle, validate_schema

ROLE_COLLECTION = {
    "seed": "seeds",
    "phase": "phases",
    "barrier": "barriers",
    "gate": "gates",
    "corridor": "corridors",
}
SCENARIO_ALIASES = {"baseline": "reviewed-baseline", "flat": "flat-natural"}


def _schema_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas"


def _safe_relative(base: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise ValueError(f"case paths must be relative: {value}")
    resolved = (base / path).resolve()
    if base.resolve() not in resolved.parents and resolved != base.resolve():
        raise ValueError(f"case path escapes the case directory: {value}")
    return resolved


def load_case(case_dir: Path) -> dict[str, Any]:
    case_dir = case_dir.resolve()
    case = load_json(case_dir / "case.json")
    required = {"case_id", "fixture_kind", "lineage_path", "grid"}
    missing = sorted(required - set(case))
    if missing:
        raise ValueError(f"case.json missing fields: {missing}")
    if case["fixture_kind"] not in {"synthetic_smoke", "public_case"}:
        raise ValueError("fixture_kind must be synthetic_smoke or public_case")
    grid = case["grid"]
    for key in ("land_path", "natural_features_path"):
        _safe_relative(case_dir, grid[key])
    _safe_relative(case_dir, case["lineage_path"])
    if case.get("scenario_config_path"):
        _safe_relative(case_dir, case["scenario_config_path"])
    return case


def normalize_scenario(value: str) -> str:
    return SCENARIO_ALIASES.get(value, value)


def scenario_names(case_dir: Path) -> list[str]:
    case = load_case(case_dir)
    path = case.get("scenario_config_path")
    if not path:
        return ["reviewed-baseline", "flat-natural"]
    config = load_json(_safe_relative(case_dir.resolve(), path))
    return sorted(config.get("scenarios", {}))


def _scenario_profile(case_dir: Path, case: dict[str, Any], scenario: str) -> tuple[str, dict[str, Any]]:
    normalized = normalize_scenario(scenario)
    path = case.get("scenario_config_path")
    if not path:
        if normalized not in {"reviewed-baseline", "flat-natural"}:
            raise ValueError(f"unsupported reconstruction scenario: {scenario}")
        return normalized, {"include_natural_costs": normalized != "flat-natural"}
    config = load_json(_safe_relative(case_dir, path))
    profiles = config.get("scenarios", {})
    if normalized not in profiles:
        raise ValueError(f"unsupported reconstruction scenario: {scenario}")
    return normalized, dict(profiles[normalized])


def _applies(decision: dict[str, Any], slice_value: int | str) -> bool:
    params = decision.get("parameters", {})
    if "slice" in params:
        return params["slice"] == slice_value
    span = params.get("time_span")
    if isinstance(slice_value, int) and isinstance(span, list) and len(span) == 2:
        return span[0] <= slice_value <= span[1]
    return True


def _seed_ids(profile: dict[str, Any], slice_value: int | str) -> set[str] | None:
    value = profile.get("seed_decision_ids")
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("seed_decision_ids must be keyed by slice")
    return set(value.get(str(slice_value), []))


def build_solver_input(
    case_dir: Path, slice_value: int | str, *, scenario: str = "reviewed-baseline"
) -> dict[str, Any]:
    case_dir = case_dir.resolve()
    case = load_case(case_dir)
    normalized, profile = _scenario_profile(case_dir, case, scenario)
    bundle = load_json(_safe_relative(case_dir, case["lineage_path"]))
    validation = validate_lineage_bundle(bundle, _schema_dir() / "lineage-bundle.schema.json")
    validation.require_ok()

    grid = dict(case["grid"])
    if "resolution" in profile:
        grid["resolution"] = profile["resolution"]
    output: dict[str, Any] = {
        "contract_version": SOLVER_INPUT_VERSION,
        "case_id": case["case_id"],
        "slice": slice_value,
        "scenario": normalized,
        "grid": grid,
        "seeds": [],
        "phases": [],
        "barriers": [],
        "gates": [],
        "corridors": [],
        "lineage": {},
    }
    for key in ("land_path", "natural_features_path"):
        _safe_relative(case_dir, output["grid"][key])

    selected_seed_ids = _seed_ids(profile, slice_value)
    decisions_by_id = {x["decision_id"]: x for x in bundle["model_decisions"]}
    if selected_seed_ids is not None:
        unknown = sorted(selected_seed_ids - set(decisions_by_id))
        if unknown:
            raise ValueError(f"scenario references unknown decisions: {unknown}")

    for decision in bundle["model_decisions"]:
        role = decision["model_role"]
        if not _applies(decision, slice_value):
            continue
        if role == "seed" and selected_seed_ids is not None:
            if decision["decision_id"] not in selected_seed_ids:
                continue
            if decision["status"] not in {"accepted", "deferred"}:
                raise ValueError(f"scenario cannot activate {decision['status']} seed {decision['decision_id']}")
        else:
            if decision["status"] not in {"accepted", "assumption"}:
                continue
            if not decision["is_allocation_input"]:
                continue
        collection = ROLE_COLLECTION.get(role)
        if not collection:
            continue
        if role == "barrier" and profile.get("include_natural_costs", True) is False:
            continue
        record = {
            "decision_id": decision["decision_id"],
            "evidence_ids": list(decision["evidence_ids"]),
            "source_ids": list(decision["source_ids"]),
            "parameters": dict(decision["parameters"]),
        }
        if decision["status"] == "assumption":
            record["assumption_reason"] = decision["assumption_reason"]
        if role == "phase" and profile.get("projection_override"):
            record["parameters"]["projection"] = profile["projection_override"]
        output[collection].append(record)
        output["lineage"][decision["decision_id"]] = [*decision["evidence_ids"], *decision["source_ids"]]

    seed_entities = {x["parameters"].get("entity") for x in output["seeds"]}
    output["phases"] = [x for x in output["phases"] if x["parameters"].get("entity") in seed_entities]
    active_decisions = {x["decision_id"] for values in (output[k] for k in ROLE_COLLECTION.values()) for x in values}
    output["lineage"] = {k: v for k, v in output["lineage"].items() if k in active_decisions}

    output["seeds"].sort(key=lambda x: (x["parameters"].get("entity", ""), x["parameters"].get("name", "")))
    output["phases"].sort(key=lambda x: x["parameters"].get("entity", ""))
    output["barriers"].sort(key=lambda x: x["parameters"].get("feature_id", ""))

    errors = validate_schema(output, _schema_dir() / "solver-input.schema.json")
    if errors:
        raise ValueError("; ".join(f"{x.path}: {x.message}" for x in errors))
    phase_entities = {x["parameters"].get("entity") for x in output["phases"]}
    missing = sorted(x for x in phase_entities - seed_entities if x)
    if missing:
        raise ValueError(f"active phase entities have no reviewed seeds: {missing}")
    if not output["phases"]:
        raise ValueError(f"scenario {normalized} has no active entities for slice {slice_value}")
    return output


def write_solver_input(
    case_dir: Path, slice_value: int | str, *, scenario: str = "reviewed-baseline"
) -> Path:
    data = build_solver_input(case_dir, slice_value, scenario=scenario)
    out_dir = case_dir.resolve() / "build"
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if data["scenario"] == "reviewed-baseline" else f"-{data['scenario']}"
    path = out_dir / f"solver-input-{slice_value}{suffix}.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
