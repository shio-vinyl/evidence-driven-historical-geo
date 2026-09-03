"""v0.2 research contracts: evidence records, uncertainty diagnoses, and search targets.

These contracts deliberately keep source material, observations, interpreted claims, and
backend-neutral model decisions separate.  JSON Schema handles record shape; this module
checks cross-record references and the research/evaluation boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator

RESEARCH_BUNDLE_VERSION = "historical_geo.research_bundle.v0.2"
UNCERTAINTY_DIAGNOSIS_VERSION = "historical_geo.uncertainty_diagnosis.v0.2"
SEARCH_TARGETS_VERSION = "historical_geo.search_targets.v0.2"

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
RESEARCH_BUNDLE_SCHEMA = SCHEMA_DIR / "research-bundle.schema.json"
UNCERTAINTY_DIAGNOSIS_SCHEMA = SCHEMA_DIR / "uncertainty-diagnosis.schema.json"
SEARCH_TARGETS_SCHEMA = SCHEMA_DIR / "search-targets.schema.json"


@dataclass(frozen=True)
class ContractIssue:
    code: str
    path: str
    message: str


@dataclass
class ValidationResult:
    errors: list[ContractIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def require_ok(self) -> None:
        if self.errors:
            summary = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in self.errors)
            raise ValueError(summary)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def validate_schema(instance: Mapping[str, Any], schema_path: Path) -> list[ContractIssue]:
    """Validate an instance against an explicit Draft 2020-12 schema."""
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    issues: list[ContractIssue] = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: tuple(map(str, item.absolute_path))):
        path = _path(error.absolute_path) or "<root>"
        issues.append(ContractIssue("schema_error", path, error.message))
    return issues


def _path(parts: Iterable[Any]) -> str:
    result = ""
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += ("." if result else "") + str(part)
    return result


def _issue(result: ValidationResult, code: str, path: str, message: str) -> None:
    result.errors.append(ContractIssue(code, path, message))


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _id_index(records: Sequence[Mapping[str, Any]], key: str) -> dict[str, Mapping[str, Any]]:
    return {str(record[key]): record for record in records if key in record}


def _check_collection_ids(
    result: ValidationResult, bundle: Mapping[str, Any], collection: str, key: str
) -> None:
    records = bundle.get(collection, [])
    if not isinstance(records, list):
        return
    for repeated in sorted(_duplicates(str(record.get(key, "")) for record in records if isinstance(record, Mapping))):
        _issue(result, "duplicate_id", collection, f"duplicate {key}: {repeated}")


def _claim_observation_ids(claim: Mapping[str, Any]) -> set[str]:
    return set(claim.get("supporting_observation_ids", [])) | set(claim.get("challenging_observation_ids", []))


def _claim_source_ids(
    claim: Mapping[str, Any], observations: Mapping[str, Mapping[str, Any]]
) -> set[str]:
    return {
        str(observations[observation_id].get("source_id"))
        for observation_id in _claim_observation_ids(claim)
        if observation_id in observations
    }


def validate_research_bundle(
    bundle: Mapping[str, Any], schema_path: Path | None = None
) -> ValidationResult:
    """Validate v0.2 research-bundle structure, references, and research use semantics."""
    result = ValidationResult()
    result.errors.extend(validate_schema(bundle, schema_path or RESEARCH_BUNDLE_SCHEMA))
    if result.errors:
        return result

    collections = {
        "sources": "source_id",
        "observations": "observation_id",
        "claims": "claim_id",
        "model_decisions": "decision_id",
        "evidence_gaps": "gap_id",
    }
    for collection, key in collections.items():
        _check_collection_ids(result, bundle, collection, key)

    sources = _id_index(bundle["sources"], "source_id")
    observations = _id_index(bundle["observations"], "observation_id")
    claims = _id_index(bundle["claims"], "claim_id")
    decisions = _id_index(bundle["model_decisions"], "decision_id")

    for index, observation in enumerate(bundle["observations"]):
        source_id = str(observation.get("source_id"))
        path = f"observations[{index}].source_id"
        source = sources.get(source_id)
        if source is None:
            _issue(result, "missing_source", path, source_id)
        elif source.get("use_role") == "evaluation_only":
            _issue(result, "evaluation_only_source_used_for_research", path, source_id)

    for index, claim in enumerate(bundle["claims"]):
        path = f"claims[{index}]"
        support = set(claim.get("supporting_observation_ids", []))
        challenge = set(claim.get("challenging_observation_ids", []))
        overlap = sorted(support & challenge)
        if overlap:
            _issue(result, "observation_both_supports_and_challenges", path, ", ".join(overlap))
        for relation, observation_ids in (
            ("supporting_observation_ids", support),
            ("challenging_observation_ids", challenge),
        ):
            for observation_id in observation_ids:
                observation = observations.get(observation_id)
                reference_path = f"{path}.{relation}"
                if observation is None:
                    _issue(result, "missing_observation", reference_path, observation_id)
                    continue
                source = sources.get(str(observation.get("source_id")))
                if source and source.get("use_role") == "evaluation_only":
                    _issue(
                        result,
                        "evaluation_only_source_used_for_research",
                        reference_path,
                        f"{observation_id} derives from {source.get('source_id')}",
                    )

    for index, decision in enumerate(bundle["model_decisions"]):
        path = f"model_decisions[{index}]"
        supporting_ids = set(decision.get("supporting_claim_ids", []))
        challenging_ids = set(decision.get("challenging_claim_ids", []))
        if supporting_ids & challenging_ids:
            _issue(
                result,
                "claim_both_supports_and_challenges_decision",
                path,
                ", ".join(sorted(supporting_ids & challenging_ids)),
            )
        for relation, claim_ids in (
            ("supporting_claim_ids", supporting_ids),
            ("challenging_claim_ids", challenging_ids),
        ):
            for claim_id in claim_ids:
                if claim_id not in claims:
                    _issue(result, "missing_claim", f"{path}.{relation}", claim_id)
        for source_id in decision.get("source_ids", []):
            source = sources.get(source_id)
            if source is None:
                _issue(result, "missing_source", f"{path}.source_ids", source_id)
            elif source.get("use_role") == "evaluation_only":
                _issue(result, "evaluation_only_source_used_for_research", f"{path}.source_ids", source_id)

        if decision.get("review_status") == "assumption" and not decision.get("assumption_reason"):
            _issue(result, "unlabeled_assumption", path, "assumption decisions require assumption_reason")
        if decision.get("review_status") == "admitted":
            if not supporting_ids:
                _issue(result, "admitted_decision_missing_support", path, "admitted decisions require a supporting claim")
            for claim_id in supporting_ids:
                claim = claims.get(claim_id)
                if claim and claim.get("status") != "supported":
                    _issue(
                        result,
                        "admitted_decision_uses_non_supported_claim",
                        f"{path}.supporting_claim_ids",
                        claim_id,
                    )

        for claim_id in supporting_ids | challenging_ids:
            claim = claims.get(claim_id)
            if claim is None:
                continue
            for source_id in _claim_source_ids(claim, observations):
                source = sources.get(source_id)
                if source and source.get("use_role") == "evaluation_only":
                    _issue(
                        result,
                        "evaluation_only_source_used_for_research",
                        f"{path}.supporting_claim_ids" if claim_id in supporting_ids else f"{path}.challenging_claim_ids",
                        f"{claim_id} derives from {source_id}",
                    )

    for index, gap in enumerate(bundle["evidence_gaps"]):
        path = f"evidence_gaps[{index}]"
        for claim_id in gap.get("related_claim_ids", []):
            if claim_id not in claims:
                _issue(result, "missing_claim", f"{path}.related_claim_ids", claim_id)
        for decision_id in gap.get("related_decision_ids", []):
            if decision_id not in decisions:
                _issue(result, "missing_decision", f"{path}.related_decision_ids", decision_id)

    return result


def _validate_bundle_references(
    result: ValidationResult,
    document: Mapping[str, Any],
    bundle: Mapping[str, Any],
    path_prefix: str = "",
    check_case_id: bool = True,
) -> None:
    if check_case_id and document.get("case_id") != bundle.get("case_id"):
        _issue(result, "case_id_mismatch", f"{path_prefix}case_id", "document and research bundle must have the same case_id")
    claims = _id_index(bundle.get("claims", []), "claim_id")
    decisions = _id_index(bundle.get("model_decisions", []), "decision_id")
    gaps = _id_index(bundle.get("evidence_gaps", []), "gap_id")
    for key, records, code in (
        ("evidence_gap_ids", gaps, "missing_evidence_gap"),
        ("claim_ids", claims, "missing_claim"),
        ("decision_ids", decisions, "missing_decision"),
    ):
        for item_id in document.get(key, []):
            if item_id not in records:
                _issue(result, code, f"{path_prefix}{key}", item_id)


def validate_uncertainty_diagnosis(
    diagnosis: Mapping[str, Any],
    bundle: Mapping[str, Any] | None = None,
    schema_path: Path | None = None,
) -> ValidationResult:
    """Validate an independent diagnosis and, when supplied, its bundle references."""
    result = ValidationResult()
    result.errors.extend(validate_schema(diagnosis, schema_path or UNCERTAINTY_DIAGNOSIS_SCHEMA))
    if result.errors:
        return result
    if bundle is not None:
        if diagnosis.get("case_id") != bundle.get("case_id"):
            _issue(
                result,
                "case_id_mismatch",
                "case_id",
                "diagnosis and research bundle must have the same case_id",
            )
        decisions = _id_index(bundle.get("model_decisions", []), "decision_id")
        for index, slice_result in enumerate(diagnosis.get("slices", [])):
            changed = slice_result.get("changed_decision_ids", {})
            for axis in ("evidence", "model", "all"):
                for decision_id in changed.get(axis, []):
                    if decision_id not in decisions:
                        _issue(
                            result,
                            "missing_decision",
                            f"slices[{index}].changed_decision_ids.{axis}",
                            decision_id,
                        )
            for axis, effects in slice_result.get("scenario_effects", {}).items():
                for effect_index, effect in enumerate(effects):
                    for decision_id in effect.get("changed_decision_ids", []):
                        if decision_id not in decisions:
                            _issue(
                                result,
                                "missing_decision",
                                f"slices[{index}].scenario_effects.{axis}[{effect_index}]"
                                ".changed_decision_ids",
                                decision_id,
                            )
    return result


def validate_search_targets(
    targets: Mapping[str, Any],
    bundle: Mapping[str, Any] | None = None,
    schema_path: Path | None = None,
) -> ValidationResult:
    """Validate independent search targets and their optional research-bundle references."""
    result = ValidationResult()
    result.errors.extend(validate_schema(targets, schema_path or SEARCH_TARGETS_SCHEMA))
    if result.errors:
        return result

    for repeated in sorted(_duplicates(str(target.get("target_id", "")) for target in targets["targets"])):
        _issue(result, "duplicate_id", "targets", f"duplicate target_id: {repeated}")
    if bundle is not None:
        if targets.get("case_id") != bundle.get("case_id"):
            _issue(result, "case_id_mismatch", "case_id", "search targets and research bundle must have the same case_id")
        for index, target in enumerate(targets["targets"]):
            _validate_bundle_references(result, target, bundle, f"targets[{index}].", check_case_id=False)
    return result


# Clear aliases for callers that use the shorter document names.
validate_diagnosis = validate_uncertainty_diagnosis
validate_search_target_bundle = validate_search_targets
