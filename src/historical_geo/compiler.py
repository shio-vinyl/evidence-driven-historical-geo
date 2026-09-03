"""Compile reviewed research decisions into a backend-neutral request.

This module deliberately knows nothing about a solver.  A backend receives the
request only after this selection boundary has made scenario choices explicit.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from historical_geo.research_contracts import validate_research_bundle, validate_schema

RECONSTRUCTION_REQUEST_VERSION = "historical_geo.reconstruction_request.v0.2"
_REVIEW_STATUSES = frozenset({"admitted", "experimental", "excluded", "assumption"})
_SCENARIO_AXES = frozenset({"baseline", "evidence", "model"})


def _schema_path() -> Path:
    return Path(__file__).resolve().parent / "schemas" / "reconstruction-request.schema.json"


def _decision_ids(profile: Mapping[str, Any], field: str, *, required: bool = False) -> set[str]:
    if required and field not in profile:
        raise ValueError(f"scenario_profile.{field} is required")
    values = profile.get(field, [])
    if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
        raise ValueError(f"scenario_profile.{field} must be a list of decision IDs")
    if len(values) != len(set(values)):
        raise ValueError(f"scenario_profile.{field} must not contain duplicates")
    return set(values)


def _profile(profile: Mapping[str, Any]) -> tuple[str, str, set[str], set[str], dict[str, Any], dict[str, Any]]:
    if not isinstance(profile, Mapping):
        raise ValueError("scenario_profile must be an object")
    name = profile.get("name")
    axis = profile.get("axis")
    if not isinstance(name, str) or not name:
        raise ValueError("scenario_profile.name must be a non-empty string")
    if axis not in _SCENARIO_AXES:
        raise ValueError(f"scenario_profile.axis must be one of {sorted(_SCENARIO_AXES)}")
    included = _decision_ids(profile, "included_decision_ids", required=True)
    excluded = _decision_ids(profile, "excluded_decision_ids")
    if included & excluded:
        raise ValueError("scenario_profile cannot both include and exclude a decision")
    parameter_overrides = profile.get("parameter_overrides", {})
    grid_overrides = profile.get("grid_overrides", {})
    if not isinstance(parameter_overrides, Mapping):
        raise ValueError("scenario_profile.parameter_overrides must be an object")
    if not isinstance(grid_overrides, Mapping):
        raise ValueError("scenario_profile.grid_overrides must be an object")
    return name, axis, included, excluded, dict(parameter_overrides), dict(grid_overrides)


def _applies_to_slice(decision: Mapping[str, Any], slice_value: int | str) -> bool:
    parameters = decision.get("parameters", {})
    if not isinstance(parameters, Mapping):
        return False
    if "slice" in parameters:
        return parameters["slice"] == slice_value
    time_span = parameters.get("time_span")
    return not (
        isinstance(slice_value, int)
        and isinstance(time_span, list)
        and len(time_span) == 2
        and all(isinstance(value, int) for value in time_span)
        and not (time_span[0] <= slice_value <= time_span[1])
    )


def _is_selected(decision: Mapping[str, Any], axis: str, included: set[str], excluded: set[str]) -> bool:
    if decision["decision_id"] in excluded:
        return False
    status = decision["review_status"]
    if status == "excluded":
        return False
    # Case profiles enumerate control points, while explicit spatial and
    # traversal assumptions remain active unless separately excluded.  Keeping
    # that distinction here prevents a newly admitted locality from silently
    # entering a reviewed scenario before its profile names it.
    if decision["role"] == "control_point" and status == "admitted":
        return decision["decision_id"] in included
    if status == "experimental":
        return axis != "baseline" and decision["decision_id"] in included
    return status in {"admitted", "assumption"}


def _input_record(decision: Mapping[str, Any], parameter_overrides: Mapping[str, Any]) -> dict[str, Any]:
    claim_ids = sorted(
        set(decision.get("supporting_claim_ids", [])) | set(decision.get("challenging_claim_ids", []))
    )
    record: dict[str, Any] = {
        "decision_id": decision["decision_id"],
        "role": decision["role"],
        "review_status": decision["review_status"],
        "claim_ids": claim_ids,
        "source_ids": sorted(set(decision.get("source_ids", []))),
        "rationale": decision["rationale"],
        "parameters": deepcopy(dict(decision["parameters"])),
    }
    if decision["review_status"] == "assumption":
        record["assumption_reason"] = decision["assumption_reason"]
    for field, value in parameter_overrides.items():
        if field in record["parameters"]:
            record["parameters"][field] = deepcopy(value)
    return record


def compile_reconstruction_request(
    research_bundle: Mapping[str, Any],
    slice_value: int | str,
    scenario_profile: Mapping[str, Any],
    grid: Mapping[str, Any],
) -> dict[str, Any]:
    """Select v0.2 research decisions for one deterministic reconstruction request.

    ``included_decision_ids`` is an explicit allowlist for control points: an
    empty list selects no control points.  Other admitted constraints and
    explicit assumptions remain active unless excluded.  Experimental
    decisions may participate in evidence/model scenarios only when named in
    the allowlist; excluded decisions can never be activated.
    """
    if not isinstance(grid, Mapping):
        raise ValueError("grid must be an object")
    validation = validate_research_bundle(research_bundle)
    validation.require_ok()
    name, axis, included, excluded, parameter_overrides, grid_overrides = _profile(scenario_profile)

    decisions = research_bundle["model_decisions"]
    known_ids = {decision["decision_id"] for decision in decisions}
    unknown = sorted((included | excluded) - known_ids)
    if unknown:
        raise ValueError(f"scenario references unknown decisions: {unknown}")

    inputs = [
        _input_record(decision, parameter_overrides)
        for decision in decisions
        if _applies_to_slice(decision, slice_value) and _is_selected(decision, axis, included, excluded)
    ]
    inputs.sort(key=lambda record: record["decision_id"])
    request = {
        "contract_version": RECONSTRUCTION_REQUEST_VERSION,
        "case_id": research_bundle["case_id"],
        "slice": slice_value,
        "scenario": name,
        "grid": {**deepcopy(dict(grid)), **deepcopy(grid_overrides)},
        "inputs": inputs,
    }
    errors = validate_schema(request, _schema_path())
    if errors:
        raise ValueError("; ".join(f"{issue.path}: {issue.message}" for issue in errors))
    return request


def reconstruction_request_bytes(request: Mapping[str, Any]) -> bytes:
    """Return the canonical serialized representation used for reproducible handoff."""
    errors = validate_schema(request, _schema_path())
    if errors:
        raise ValueError("; ".join(f"{issue.path}: {issue.message}" for issue in errors))
    return (json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
