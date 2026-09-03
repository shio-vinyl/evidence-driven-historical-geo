"""Pure translation from a generic reconstruction request to legacy XTENT input."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from historical_geo.contracts import SOLVER_INPUT_VERSION

_REQUEST_VERSION = "historical_geo.reconstruction_request.v0.2"


def _require_parameters(record: Mapping[str, Any], *names: str) -> dict[str, Any]:
    parameters = record.get("parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError(f"{record.get('decision_id', '<unknown>')}: parameters must be an object")
    missing = [name for name in names if name not in parameters or parameters[name] in (None, "")]
    if missing:
        raise ValueError(f"{record.get('decision_id', '<unknown>')}: missing required parameters: {', '.join(missing)}")
    return dict(parameters)


def _legacy_record(record: Mapping[str, Any], parameters: Mapping[str, Any] | None = None) -> dict[str, Any]:
    output = {
        "decision_id": record["decision_id"],
        # The legacy contract calls these evidence IDs. They carry claim IDs here,
        # while the combined, lossless lineage remains available at top level.
        "evidence_ids": list(record["claim_ids"]),
        "source_ids": list(record["source_ids"]),
        "parameters": deepcopy(dict(parameters if parameters is not None else record["parameters"])),
    }
    if record.get("review_status") == "assumption":
        output["assumption_reason"] = record["assumption_reason"]
    return output


def _convert_record(record: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    role = record.get("role")
    if role == "control_point":
        parameters = _require_parameters(record, "entity", "name", "coordinates", "weight_class")
        parameters["weight_ordinal"] = parameters.pop("weight_class")
        return "seeds", _legacy_record(record, parameters)
    if role == "spatial_constraint":
        parameters = _require_parameters(record, "constraint_kind", "entity", "reach_class")
        if parameters["constraint_kind"] != "extent_prior":
            raise ValueError(
                f"{record.get('decision_id', '<unknown>')}: unsupported spatial constraint kind "
                f"{parameters['constraint_kind']!r}"
            )
        parameters.pop("constraint_kind")
        parameters["projection"] = parameters.pop("reach_class")
        return "phases", _legacy_record(record, parameters)
    if role == "traversal_constraint":
        parameters = _require_parameters(record, "constraint_kind", "feature_id", "strength")
        if parameters["constraint_kind"] != "friction_feature":
            raise ValueError(
                f"{record.get('decision_id', '<unknown>')}: unsupported traversal constraint kind "
                f"{parameters['constraint_kind']!r}"
            )
        parameters.pop("constraint_kind")
        return "barriers", _legacy_record(record, parameters)
    raise ValueError(f"{record.get('decision_id', '<unknown>')}: XTENT does not support role {role!r}")


def compile_xtent_solver_input(request: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a validated generic request without invoking the XTENT solver."""
    if not isinstance(request, Mapping) or request.get("contract_version") != _REQUEST_VERSION:
        raise ValueError(f"request must use {_REQUEST_VERSION}")
    required = ("case_id", "slice", "scenario", "grid", "inputs")
    missing = [name for name in required if name not in request]
    if missing:
        raise ValueError(f"request missing fields: {', '.join(missing)}")
    if not isinstance(request["grid"], Mapping) or not isinstance(request["inputs"], list):
        raise ValueError("request.grid must be an object and request.inputs must be a list")

    output: dict[str, Any] = {
        "contract_version": SOLVER_INPUT_VERSION,
        "case_id": request["case_id"],
        "slice": request["slice"],
        "scenario": request["scenario"],
        "grid": deepcopy(dict(request["grid"])),
        "seeds": [],
        "phases": [],
        "barriers": [],
        "gates": [],
        "corridors": [],
        "lineage": {},
    }
    for record in request["inputs"]:
        if not isinstance(record, Mapping):
            raise ValueError("request inputs must be objects")
        required_record = ("decision_id", "claim_ids", "source_ids", "parameters")
        missing_record = [name for name in required_record if name not in record]
        if missing_record:
            raise ValueError(f"request input missing fields: {', '.join(missing_record)}")
        if not isinstance(record["claim_ids"], list) or not isinstance(record["source_ids"], list):
            raise ValueError(f"{record['decision_id']}: claim_ids and source_ids must be lists")
        collection, legacy = _convert_record(record)
        output[collection].append(legacy)
        output["lineage"][record["decision_id"]] = sorted(set(record["claim_ids"]) | set(record["source_ids"]))

    active_entities = {seed["parameters"]["entity"] for seed in output["seeds"]}
    removed_phase_ids = {
        phase["decision_id"] for phase in output["phases"] if phase["parameters"]["entity"] not in active_entities
    }
    output["phases"] = [
        phase for phase in output["phases"] if phase["parameters"]["entity"] in active_entities
    ]
    for decision_id in removed_phase_ids:
        output["lineage"].pop(decision_id, None)

    output["seeds"].sort(key=lambda value: (value["parameters"]["entity"], value["parameters"]["name"], value["decision_id"]))
    output["phases"].sort(key=lambda value: (value["parameters"]["entity"], value["decision_id"]))
    output["barriers"].sort(key=lambda value: (value["parameters"]["feature_id"], value["decision_id"]))
    output["lineage"] = {key: output["lineage"][key] for key in sorted(output["lineage"])}
    return output


__all__ = ["compile_xtent_solver_input"]
