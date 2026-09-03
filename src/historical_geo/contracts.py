"""Public v0.1 lineage contracts and semantic validation."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

LINEAGE_VERSION = "historical_geo.lineage.v0.1"
SOLVER_INPUT_VERSION = "historical_geo.solver_input.v0.1"
RUN_VERSION = "historical_geo.run.v0.1"
CALIBRATION_VERSION = "xtent-ordinal-v0.1"

PROJECTION_ORDINALS = frozenset({"expansive", "normal", "contracted"})
SEED_WEIGHT_ORDINALS = frozenset({"capital", "major", "minor", "outpost"})
BARRIER_STRENGTH_ORDINALS = frozenset({"hard", "soft", "porous"})
CORRIDOR_WIDTH_ORDINALS = frozenset({"narrow", "normal"})
COORDINATE_STATUS = frozenset({"verified", "approximate", "unknown"})

ALLOCATION_ROLES = frozenset({"seed", "phase", "barrier", "gate", "corridor"})
NON_AREAL_ROLES = frozenset({"event", "frontier", "disputed", "influence", "claim", "display_context"})
ORDINAL_RULES = {
    "projection": PROJECTION_ORDINALS,
    "weight_ordinal": SEED_WEIGHT_ORDINALS,
    "strength": BARRIER_STRENGTH_ORDINALS,
    "width": CORRIDOR_WIDTH_ORDINALS,
    "coordinates_status": COORDINATE_STATUS,
}
MODEL_NUMERIC_FIELDS = frozenset({"slice"})
MODEL_NUMERIC_LIST_FIELDS = frozenset({"coordinates", "time_span"})


@dataclass(frozen=True)
class ContractIssue:
    code: str
    path: str
    message: str


@dataclass
class ValidationResult:
    errors: list[ContractIssue] = field(default_factory=list)
    research_gaps: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def require_ok(self) -> None:
        if self.errors:
            summary = "; ".join(f"{x.code} at {x.path}: {x.message}" for x in self.errors)
            raise ValueError(summary)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def validate_schema(instance: dict[str, Any], schema_path: Path) -> list[ContractIssue]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    issues: list[ContractIssue] = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: ".".join(str(x) for x in item.absolute_path)):
        path = ".".join(str(x) for x in error.absolute_path) or "<root>"
        issues.append(ContractIssue("schema_error", path, error.message))
    return issues


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def _issue(result: ValidationResult, code: str, path: str, message: str) -> None:
    result.errors.append(ContractIssue(code, path, message))


def _validate_ordinals(value: Any, path: str, result: ValidationResult) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in ORDINAL_RULES:
                allowed = ORDINAL_RULES[key]
                if not isinstance(child, str) or child not in allowed:
                    _issue(result, "unsupported_ordinal", child_path, f"expected one of {sorted(allowed)}")
                continue
            if isinstance(child, (int, float)) and not isinstance(child, bool) and key not in MODEL_NUMERIC_FIELDS:
                _issue(result, "raw_number_forbidden", child_path, "model tuning must use a bounded ordinal")
                continue
            if key in MODEL_NUMERIC_LIST_FIELDS and isinstance(child, list):
                if not all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in child):
                    _issue(result, "invalid_numeric_list", child_path, f"{key} must contain numbers only")
                continue
            _validate_ordinals(child, child_path, result)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_ordinals(child, f"{path}[{index}]", result)


def _decision_evidence(decision: dict[str, Any], evidence_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [evidence_by_id[x] for x in decision.get("evidence_ids", []) if x in evidence_by_id]


def validate_lineage_bundle(bundle: dict[str, Any], schema_path: Path | None = None) -> ValidationResult:
    result = ValidationResult()
    if schema_path:
        result.errors.extend(validate_schema(bundle, schema_path))
        if result.errors:
            return result

    collections = {
        "sources": "source_id",
        "observations": "observation_id",
        "evidence_claims": "evidence_id",
        "model_decisions": "decision_id",
    }
    for name, key in collections.items():
        repeated = _duplicates(str(x.get(key, "")) for x in bundle.get(name, []))
        for item_id in sorted(repeated):
            _issue(result, "duplicate_id", name, f"duplicate {key}: {item_id}")

    sources = {x["source_id"]: x for x in bundle.get("sources", [])}
    observations = {x["observation_id"]: x for x in bundle.get("observations", [])}
    evidence = {x["evidence_id"]: x for x in bundle.get("evidence_claims", [])}

    for index, observation in enumerate(bundle.get("observations", [])):
        source_id = observation.get("source_id")
        if source_id not in sources:
            _issue(result, "missing_source", f"observations[{index}].source_id", str(source_id))

    for index, claim in enumerate(bundle.get("evidence_claims", [])):
        for observation_id in claim.get("observation_ids", []):
            if observation_id not in observations:
                _issue(result, "missing_observation", f"evidence_claims[{index}].observation_ids", observation_id)

    for index, decision in enumerate(bundle.get("model_decisions", [])):
        path = f"model_decisions[{index}]"
        status = decision.get("status")
        role = decision.get("model_role")
        allocation = decision.get("is_allocation_input") is True
        evidence_ids = decision.get("evidence_ids", [])
        source_ids = decision.get("source_ids", [])

        for evidence_id in evidence_ids:
            if evidence_id not in evidence:
                _issue(result, "missing_evidence", f"{path}.evidence_ids", evidence_id)
        for source_id in source_ids:
            if source_id not in sources:
                _issue(result, "missing_source", f"{path}.source_ids", source_id)

        if status == "assumption":
            if not decision.get("assumption_reason"):
                _issue(result, "unlabeled_assumption", path, "assumptions require assumption_reason")
        elif status == "accepted" and role != "research_gap" and not evidence_ids:
            _issue(result, "missing_evidence", path, "accepted decisions require evidence_ids")
            result.research_gaps.append({
                "decision_id": decision.get("decision_id"),
                "gap_type": "missing_evidence",
                "required_for": role,
                "question": "Which reviewed evidence supports this model decision?",
            })

        if status in {"excluded", "deferred"} and allocation:
            _issue(result, "inactive_decision_is_allocation_input", path, "excluded/deferred decisions cannot enter allocation")
        if role == "display_only" and allocation:
            _issue(result, "display_enters_allocation", path, "display-only decisions cannot enter allocation")
        if allocation and role not in ALLOCATION_ROLES:
            _issue(result, "unsupported_allocation_role", path, f"{role!r} is not an allocation role")

        supporting = _decision_evidence(decision, evidence)
        semantics = {x.get("semantic_role") for x in supporting}
        linked_sources = {
            observations[observation_id]["source_id"]
            for claim in supporting
            for observation_id in claim.get("observation_ids", [])
            if observation_id in observations
        }
        missing_linked_sources = sorted(linked_sources - set(source_ids))
        if missing_linked_sources:
            _issue(result, "incomplete_source_lineage", f"{path}.source_ids", f"missing evidence source IDs {missing_linked_sources}")
        if allocation and role == "seed" and semantics and semantics != {"point_control"}:
            _issue(result, "non_point_seed", path, f"seed evidence must be point_control, got {sorted(semantics)}")
        if allocation and role == "seed" and status in {"accepted", "assumption"}:
            params = decision.get("parameters", {})
            coords = params.get("coordinates")
            if not isinstance(coords, list) or len(coords) != 2:
                _issue(result, "missing_seed_coordinates", f"{path}.parameters.coordinates", "seed requires [longitude, latitude]")
            if params.get("coordinates_status") == "unknown":
                _issue(result, "unknown_coordinates", path, "unknown coordinates cannot become a seed")
        if allocation and role in {"phase", "barrier", "gate"} and semantics.intersection(NON_AREAL_ROLES):
            _issue(result, "non_areal_allocation", path, f"non-areal semantics cannot support {role}")
        if allocation and role == "corridor" and semantics and not semantics.issubset({"route_control", "point_control", "area_control"}):
            _issue(result, "unsupported_corridor_evidence", path, f"corridor evidence has unsupported semantics {sorted(semantics)}")
        if allocation and role == "barrier" and status != "assumption" and "natural_barrier" not in semantics:
            _issue(result, "unsupported_natural_role", path, "barrier requires natural_barrier evidence or an explicit assumption")
        if allocation and role == "boundary_attractor" and status != "assumption" and "natural_boundary" not in semantics:
            _issue(result, "unsupported_natural_role", path, "boundary attractor requires natural_boundary evidence or an explicit assumption")

        _validate_ordinals(decision.get("parameters", {}), f"{path}.parameters", result)

    return result
