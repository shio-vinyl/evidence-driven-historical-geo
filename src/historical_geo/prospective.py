"""Validation gates for prospective cases before held-out material is opened."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from historical_geo.research_contracts import (
    ContractIssue,
    ValidationResult,
    load_json,
    validate_research_bundle,
    validate_schema,
)

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
PREREGISTRATION_SCHEMA = SCHEMA_DIR / "preregistration.schema.json"
HELD_OUT_REGISTER_SCHEMA = SCHEMA_DIR / "held-out-map-register.schema.json"
LIFECYCLE_SCHEMA = SCHEMA_DIR / "prospective-lifecycle.schema.json"
SEALED_STAGES = frozenset({"preregistered", "evidence_collection", "reconstructed_pre_evaluation"})
TERMINAL_STAGES = frozenset({"completed_no_reconstruction"})
MAP_BODY_SUFFIXES = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".svg"})
ROUND_FILES = frozenset({
    "round.json",
    "queries.json",
    "sources.json",
    "observations.json",
    "claims.json",
    "decisions.json",
    "gaps.json",
    "budget.json",
    "gate.json",
})
ALLOWED_TRANSITIONS = {
    "preregistered": frozenset({"evidence_collection"}),
    "evidence_collection": frozenset({
        "evidence_collection",
        "reconstructed_pre_evaluation",
        "completed_no_reconstruction",
    }),
    "reconstructed_pre_evaluation": frozenset({"evaluation_opened"}),
    "evaluation_opened": frozenset(),
    "completed_no_reconstruction": frozenset(),
}


def _issue(result: ValidationResult, code: str, path: str, message: str) -> None:
    result.errors.append(ContractIssue(code, path, message))


def _load(case_dir: Path, case: Mapping[str, Any], field: str) -> dict[str, Any]:
    return load_json(case_dir / str(case[field]))


def _canonical_text(document: Any) -> str:
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _baseline_state_sha256(case_id: str, freeze_commit: str, freeze: Mapping[str, Any]) -> str:
    state = {
        "case_id": case_id,
        "freeze_commit": freeze_commit,
        "frozen_artifacts": freeze.get("frozen_artifacts", []),
    }
    return _sha256_bytes(_canonical_text(state).encode("utf-8"))


def _safe_file(case_dir: Path, relative: str) -> Path | None:
    path = Path(relative)
    if path.is_absolute():
        return None
    resolved = (case_dir / path).resolve()
    return resolved if case_dir == resolved or case_dir in resolved.parents else None


def validate_preregistration(document: Mapping[str, Any]) -> ValidationResult:
    result = ValidationResult()
    result.errors.extend(validate_schema(document, PREREGISTRATION_SCHEMA))
    if result.errors:
        return result
    temporal = document.get("temporal_scope", {})
    if temporal.get("temporal_resolution") == "campaign_horizon":
        if document.get("contract_version") != "historical_geo.preregistration.v0.2":
            _issue(
                result,
                "bce_contract_version_mismatch",
                "contract_version",
                "campaign-horizon BCE dates require preregistration v0.2",
            )
        year_bce = temporal.get("year_bce")
        equivalent = temporal.get("astronomical_year_numbering", {}).get("equivalent_year")
        if isinstance(year_bce, int) and equivalent != astronomical_year_from_bce(year_bce):
            _issue(
                result,
                "astronomical_year_mismatch",
                "temporal_scope.astronomical_year_numbering.equivalent_year",
                f"expected {astronomical_year_from_bce(year_bce)} for {year_bce} BCE",
            )
        negative_iso = re.compile(r"^-\d{4,}-\d{2}-\d{2}$")
        for path, value in _walk_strings(temporal):
            if negative_iso.fullmatch(value):
                _issue(
                    result,
                    "negative_iso_bce_date",
                    f"temporal_scope{path}",
                    "BCE dates must use era/year_bce fields, not negative ISO years",
                )
    return result


def astronomical_year_from_bce(year_bce: int) -> int:
    """Convert a positive BCE year label to astronomical year numbering."""
    if isinstance(year_bce, bool) or not isinstance(year_bce, int) or year_bce < 1:
        raise ValueError("year_bce must be a positive integer")
    return 1 - year_bce


def _walk_strings(value: Any, path: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        found.append((path, value))
    elif isinstance(value, Mapping):
        for key, item in value.items():
            found.extend(_walk_strings(item, f".{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_walk_strings(item, f"[{index}]"))
    return found


def validate_held_out_register(document: Mapping[str, Any]) -> ValidationResult:
    result = ValidationResult()
    result.errors.extend(validate_schema(document, HELD_OUT_REGISTER_SCHEMA))
    if result.errors:
        return result
    candidates = document["candidates"]
    ids = [candidate["reference_id"] for candidate in candidates]
    if len(ids) != len(set(ids)):
        _issue(result, "duplicate_id", "candidates", "held-out reference IDs must be unique")
    if document["candidate_order"] != ids:
        _issue(result, "candidate_order_mismatch", "candidate_order", "must match candidates in priority order")
    if document["primary_candidate_id"] != ids[0]:
        _issue(result, "primary_candidate_mismatch", "primary_candidate_id", "must be first in candidate_order")
    for index, candidate in enumerate(candidates):
        expected = "primary" if index == 0 else "fallback"
        if candidate["selection_role"] != expected:
            _issue(result, "candidate_role_mismatch", f"candidates[{index}].selection_role", f"expected {expected}")
    return result


def _load_round_files(round_dir: Path, result: ValidationResult) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for name in sorted(ROUND_FILES):
        path = round_dir / name
        try:
            documents[name] = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            _issue(result, "missing_or_invalid_round_file", str(path), str(exc))
    return documents


def _validate_source_round(
    documents: Mapping[str, Mapping[str, Any]],
    baseline_source_ids: set[str],
    known_gap_ids: set[str],
    seen_source_ids: set[str],
    admitted_source_ids: set[str],
    seen_observation_ids: set[str],
    seen_claim_ids: set[str],
    seen_decision_ids: set[str],
    result: ValidationResult,
    prefix: str,
) -> dict[str, Any]:
    queries = documents.get("queries.json", {}).get("queries", [])
    sources_doc = documents.get("sources.json", {})
    sources = sources_doc.get("records", [])
    checks = sources_doc.get("content_checks", [])
    observations = documents.get("observations.json", {}).get("observations", [])
    claims = documents.get("claims.json", {}).get("claims", [])
    decisions = documents.get("decisions.json", {}).get("decisions", [])
    gaps = documents.get("gaps.json", {}).get("gap_updates", [])
    budget = documents.get("budget.json", {})

    query_ids = [item.get("query_id") for item in queries if isinstance(item, Mapping)]
    if len(query_ids) != len(set(query_ids)) or any(not value for value in query_ids):
        _issue(result, "duplicate_or_missing_query_id", f"{prefix}/queries.json", "query IDs must be non-empty and unique")
    for index, query in enumerate(queries):
        if not isinstance(query, Mapping):
            _issue(result, "invalid_query", f"{prefix}/queries.json:queries[{index}]", "must be an object")
            continue
        if not isinstance(query.get("query"), str) or not query.get("query", "").strip():
            _issue(result, "missing_query_text", f"{prefix}/queries.json:queries[{index}]", "exact query text is required")
        gap_ids = set(query.get("gap_ids", []))
        if not gap_ids or gap_ids - known_gap_ids:
            _issue(result, "invalid_query_gap", f"{prefix}/queries.json:queries[{index}]", str(sorted(gap_ids - known_gap_ids)))
        if query.get("follow_up_round") not in {None, 1, 2}:
            _issue(result, "invalid_follow_up_round", f"{prefix}/queries.json:queries[{index}]", "must be null, 1, or 2")

    source_ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
    if len(source_ids) != len(set(source_ids)) or any(not value for value in source_ids):
        _issue(result, "duplicate_or_missing_source_id", f"{prefix}/sources.json", "source IDs must be non-empty and unique")
    duplicates = (set(source_ids) & baseline_source_ids) | (set(source_ids) & seen_source_ids)
    if duplicates:
        _issue(result, "non_append_only_source", f"{prefix}/sources.json", str(sorted(duplicates)))
    source_by_id = {item.get("source_id"): item for item in sources if isinstance(item, Mapping)}
    required_source_fields = {
        "query_ids", "access_date", "url", "locator", "content_access_scope",
        "rights_status", "atomic_observation", "disposition", "disposition_reason",
        "lineage_id", "gap_ids", "map_body_accessed",
    }
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            _issue(result, "invalid_source_record", f"{prefix}/sources.json:records[{index}]", "must be an object")
            continue
        missing = sorted(required_source_fields - set(source))
        if missing:
            _issue(result, "incomplete_source_record", f"{prefix}/sources.json:records[{index}]", str(missing))
        if source.get("map_body_accessed") is not False:
            _issue(result, "map_body_accessed_by_research_source", f"{prefix}/sources.json:records[{index}]", "must be false")
        if source.get("disposition") not in {"admitted", "rejected"}:
            _issue(result, "invalid_source_disposition", f"{prefix}/sources.json:records[{index}]", "must be admitted or rejected")
        if not set(source.get("query_ids", [])) <= set(query_ids):
            _issue(result, "unknown_source_query", f"{prefix}/sources.json:records[{index}]", str(source.get("query_ids")))
        if not set(source.get("gap_ids", [])) or set(source.get("gap_ids", [])) - known_gap_ids:
            _issue(result, "invalid_source_gap", f"{prefix}/sources.json:records[{index}]", str(source.get("gap_ids")))
        for field in ("access_date", "url", "locator", "content_access_scope", "rights_status", "atomic_observation", "disposition_reason", "lineage_id"):
            if not isinstance(source.get(field), str) or not source.get(field, "").strip():
                _issue(result, "incomplete_source_record", f"{prefix}/sources.json:records[{index}].{field}", "non-empty text is required")

    check_ids: set[str] = set()
    for index, check in enumerate(checks):
        path = f"{prefix}/sources.json:content_checks[{index}]"
        if not isinstance(check, Mapping) or not check.get("check_id"):
            _issue(result, "invalid_content_check", path, "check ID is required")
            continue
        if check["check_id"] in check_ids:
            _issue(result, "duplicate_content_check", path, str(check["check_id"]))
        check_ids.add(check["check_id"])
        if check.get("source_id") not in source_by_id:
            _issue(result, "unknown_checked_source", path, str(check.get("source_id")))
        if check.get("map_body_accessed") is not False:
            _issue(result, "map_body_accessed_by_research_source", path, "must be false")

    admitted_ids = {source_id for source_id, source in source_by_id.items() if source.get("disposition") == "admitted"}
    observation_ids = [item.get("observation_id") for item in observations if isinstance(item, Mapping)]
    if len(observation_ids) != len(set(observation_ids)) or set(observation_ids) & seen_observation_ids:
        _issue(result, "non_append_only_observation", f"{prefix}/observations.json", "observation IDs must be new and unique")
    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            _issue(result, "invalid_observation", f"{prefix}/observations.json:observations[{index}]", "must be an object")
            continue
        if observation.get("source_id") not in admitted_ids:
            _issue(result, "observation_from_unadmitted_source", f"{prefix}/observations.json:observations[{index}]", str(observation.get("source_id")))
        if not observation.get("locator") or not observation.get("paraphrase"):
            _issue(result, "incomplete_observation", f"{prefix}/observations.json:observations[{index}]", "locator and paraphrase are required")

    available_observations = seen_observation_ids | set(observation_ids)
    claim_ids = [item.get("claim_id") for item in claims if isinstance(item, Mapping)]
    if len(claim_ids) != len(set(claim_ids)) or set(claim_ids) & seen_claim_ids:
        _issue(result, "non_append_only_claim", f"{prefix}/claims.json", "claim IDs must be new and unique")
    for index, claim in enumerate(claims):
        if not isinstance(claim, Mapping):
            _issue(result, "invalid_claim", f"{prefix}/claims.json:claims[{index}]", "must be an object")
            continue
        refs = set(claim.get("supporting_observation_ids", [])) | set(claim.get("challenging_observation_ids", []))
        if not refs or refs - available_observations:
            _issue(result, "invalid_claim_observation", f"{prefix}/claims.json:claims[{index}]", str(sorted(refs - available_observations)))

    available_claims = seen_claim_ids | set(claim_ids)
    decision_ids = [item.get("decision_id") for item in decisions if isinstance(item, Mapping)]
    if len(decision_ids) != len(set(decision_ids)) or set(decision_ids) & seen_decision_ids:
        _issue(result, "non_append_only_decision", f"{prefix}/decisions.json", "decision IDs must be new and unique")
    for index, decision in enumerate(decisions):
        if not isinstance(decision, Mapping):
            _issue(result, "invalid_decision", f"{prefix}/decisions.json:decisions[{index}]", "must be an object")
            continue
        refs = set(decision.get("supporting_claim_ids", [])) | set(decision.get("challenging_claim_ids", []))
        if not refs or refs - available_claims:
            _issue(result, "invalid_decision_claim", f"{prefix}/decisions.json:decisions[{index}]", str(sorted(refs - available_claims)))
        if not set(decision.get("source_ids", [])) <= (baseline_source_ids | admitted_source_ids | admitted_ids):
            _issue(result, "invalid_decision_source", f"{prefix}/decisions.json:decisions[{index}]", str(decision.get("source_ids")))

    gap_ids = [item.get("gap_id") for item in gaps if isinstance(item, Mapping)]
    if len(gap_ids) != len(set(gap_ids)) or set(gap_ids) - known_gap_ids:
        _issue(result, "invalid_gap_update", f"{prefix}/gaps.json", str(sorted(set(gap_ids) - known_gap_ids)))
    allowed_gap_statuses = {"open", "closed_supported", "closed_unresolved", "closed_excluded"}
    for index, gap in enumerate(gaps):
        if not isinstance(gap, Mapping):
            _issue(result, "invalid_gap_update", f"{prefix}/gaps.json:gap_updates[{index}]", "must be an object")
            continue
        if gap.get("status") not in allowed_gap_statuses or not gap.get("rationale"):
            _issue(result, "invalid_gap_update", f"{prefix}/gaps.json:gap_updates[{index}]", "invalid status or missing rationale")

    derived_follow_ups = {
        gap_id: len({
            query.get("follow_up_round")
            for query in queries
            if isinstance(query, Mapping)
            and gap_id in query.get("gap_ids", [])
            and query.get("follow_up_round") in {1, 2}
        })
        for gap_id in known_gap_ids
    }
    consumed = budget.get("consumed", {})
    expected = {
        "queries": len(queries),
        "content_record_checks": len(checks),
        "sources_admitted": len(admitted_ids),
    }
    for name, value in expected.items():
        if consumed.get(name) != value:
            _issue(result, "budget_ledger_mismatch", f"{prefix}/budget.json:consumed.{name}", f"expected {value}")
    if consumed.get("per_gap_follow_ups") != derived_follow_ups:
        _issue(result, "budget_ledger_mismatch", f"{prefix}/budget.json:consumed.per_gap_follow_ups", f"expected {derived_follow_ups}")

    seen_source_ids.update(source_ids)
    admitted_source_ids.update(admitted_ids)
    seen_observation_ids.update(observation_ids)
    seen_claim_ids.update(claim_ids)
    seen_decision_ids.update(decision_ids)
    return {
        "queries": len(queries),
        "content_record_checks": len(checks),
        "sources_admitted": len(admitted_ids),
        "per_gap_follow_ups": derived_follow_ups,
        "gap_updates": gaps,
        "documents": documents,
    }


def effective_prospective_state(case_dir: Path, case: Mapping[str, Any]) -> dict[str, Any]:
    """Materialize the frozen baseline plus every reviewed append-only round."""
    case_dir = case_dir.resolve()
    bundle = _load(case_dir, case, "research_bundle_path")
    lifecycle = load_json(case_dir / "lifecycle.json")
    state = {
        "stage": case["research_stage"],
        "reconstruction_ready": bool(case["reconstruction_ready"]),
        "terminal_outcome": None,
        "sources": list(bundle.get("sources", [])),
        "observations": list(bundle.get("observations", [])),
        "claims": list(bundle.get("claims", [])),
        "model_decisions": list(bundle.get("model_decisions", [])),
        "gap_statuses": {gap["gap_id"]: gap["status"] for gap in bundle.get("evidence_gaps", [])},
    }
    for entry in lifecycle.get("rounds", []):
        round_dir = _safe_file(case_dir, str(entry.get("path", "")))
        if round_dir is None or not round_dir.is_dir():
            continue
        documents = {name: load_json(round_dir / name) for name in ROUND_FILES if (round_dir / name).is_file()}
        sources = documents.get("sources.json", {}).get("records", [])
        state["sources"].extend(source for source in sources if source.get("disposition") == "admitted")
        state["observations"].extend(documents.get("observations.json", {}).get("observations", []))
        state["claims"].extend(documents.get("claims.json", {}).get("claims", []))
        state["model_decisions"].extend(documents.get("decisions.json", {}).get("decisions", []))
        for update in documents.get("gaps.json", {}).get("gap_updates", []):
            state["gap_statuses"][update["gap_id"]] = update["status"]
        transition = documents.get("round.json", {}).get("transition", {})
        state["stage"] = transition.get("to", state["stage"])
        state["reconstruction_ready"] = bool(transition.get("reconstruction_ready", state["reconstruction_ready"]))
        state["terminal_outcome"] = transition.get("terminal_outcome")
    return state


def validate_prospective_case(case_dir: Path, case: Mapping[str, Any]) -> ValidationResult:
    """Validate lifecycle, freeze integrity, and the sealed research/evaluation boundary."""
    case_dir = case_dir.resolve()
    result = ValidationResult()
    try:
        prereg = _load(case_dir, case, "preregistration_path")
        held_out = _load(case_dir, case, "held_out_map_register_path")
        bundle = _load(case_dir, case, "research_bundle_path")
        scenarios = _load(case_dir, case, "research_scenarios_path")
        source_access = _load(case_dir, case, "source_access_path")
        spatial_contract = _load(case_dir, case, "spatial_input_contract_path")
        gap_register = _load(case_dir, case, "evidence_gap_register_path")
        freeze = _load(case_dir, case, "freeze_manifest_path")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        _issue(result, "missing_or_invalid_artifact", "case.json", str(exc))
        return result

    result.errors.extend(validate_preregistration(prereg).errors)
    result.errors.extend(validate_held_out_register(held_out).errors)
    result.errors.extend(validate_research_bundle(bundle).errors)
    case_id = case.get("case_id")
    for name, document in (
        ("preregistration", prereg),
        ("held-out-map-register", held_out),
        ("research-bundle", bundle),
        ("research-scenarios", scenarios),
        ("source-access", source_access),
        ("spatial-input-contract", spatial_contract),
        ("evidence-gap-register", gap_register),
        ("preregistration-freeze", freeze),
    ):
        if document.get("case_id") != case_id:
            _issue(result, "case_id_mismatch", name, f"expected {case_id!r}")

    if prereg.get("research_stage") != case.get("research_stage"):
        _issue(result, "stage_mismatch", "preregistration.research_stage", "must match case.json")
    if bool(prereg.get("reconstruction_ready")) != bool(case.get("reconstruction_ready")):
        _issue(result, "readiness_mismatch", "preregistration.reconstruction_ready", "must match case.json")

    expected_gaps = [
        {"gap_id": gap.get("gap_id"), "status": gap.get("status")}
        for gap in bundle.get("evidence_gaps", [])
    ]
    if gap_register.get("authoritative_source") != "research-bundle.json#/evidence_gaps":
        _issue(result, "invalid_gap_register_source", "evidence-gap-register.authoritative_source", "must point to the research bundle")
    if gap_register.get("entries") != expected_gaps:
        _issue(result, "gap_register_mismatch", "evidence-gap-register.entries", "IDs and statuses must mirror the authoritative bundle order")

    held_out_tokens: set[str] = set(held_out.get("candidate_order", []))
    for candidate in held_out.get("candidates", []):
        held_out_tokens.update({
            str(candidate.get("title", "")),
            str(candidate.get("catalog_url", "")),
            str(candidate.get("identifier", {}).get("value", "")),
        })
    held_out_tokens.discard("")
    restricted_documents = {
        "research-bundle.json": bundle,
        "research-scenarios.json": scenarios,
        "source-access-rights.json": source_access,
        "spatial-input-contract.json": spatial_contract,
        "evidence-gap-register.json": gap_register,
    }
    for name, document in restricted_documents.items():
        text = _canonical_text(document)
        for token in held_out_tokens:
            if token in text:
                _issue(result, "held_out_reference_leak", name, token)

    access_by_id = {
        record.get("source_id"): record for record in source_access.get("records", []) if isinstance(record, Mapping)
    }
    for index, access in enumerate(source_access.get("records", [])):
        if access.get("map_body_accessed") is not False:
            _issue(result, "map_body_accessed_by_research_source", f"source-access.records[{index}]", "must be false")
    for index, source in enumerate(bundle.get("sources", [])):
        source_id = source.get("source_id")
        access = access_by_id.get(source_id)
        if access is None:
            _issue(result, "missing_source_access_record", f"research-bundle.sources[{index}]", str(source_id))
            continue
        if access.get("evidence_class") == "historical_territorial_map" or source.get("source_type") == "map":
            _issue(result, "territorial_map_in_research_bundle", f"research-bundle.sources[{index}]", str(source_id))
        if access.get("content_access") not in {"full_text", "record_text", "abstract_only"}:
            _issue(result, "invalid_research_access_scope", f"source-access.records[{source_id}]", "research sources need a declared textual access scope")

    decision_ids = {item.get("decision_id") for item in bundle.get("model_decisions", [])}
    for name, profile in scenarios.get("scenarios", {}).items():
        included = set(profile.get("included_decision_ids", []))
        excluded = set(profile.get("excluded_decision_ids", []))
        unknown = sorted((included | excluded) - decision_ids)
        if unknown:
            _issue(result, "unknown_scenario_decision", f"research-scenarios.scenarios.{name}", str(unknown))
        if included & excluded:
            _issue(result, "scenario_decision_conflict", f"research-scenarios.scenarios.{name}", str(sorted(included & excluded)))
    if scenarios.get("baseline") not in scenarios.get("scenarios", {}):
        _issue(result, "missing_baseline_scenario", "research-scenarios.baseline", "baseline profile is absent")

    stage = str(case.get("research_stage"))
    if stage in SEALED_STAGES:
        if held_out.get("isolation_state") != "metadata_only_unviewed":
            _issue(result, "held_out_state_mismatch", "held-out-map-register.isolation_state", "sealed stages require metadata_only_unviewed")
        for index, candidate in enumerate(held_out.get("candidates", [])):
            for flag in ("body_viewed", "thumbnail_viewed", "downloaded", "ocr_performed", "screen_captured"):
                if candidate.get(flag) is not False:
                    _issue(result, "held_out_content_accessed", f"held-out-map-register.candidates[{index}].{flag}", "must remain false before evaluation opens")
            if candidate.get("content_access_status") != "not_viewed":
                _issue(result, "held_out_content_accessed", f"held-out-map-register.candidates[{index}].content_access_status", "must remain not_viewed")
        for path in case_dir.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(case_dir)
            if path.suffix.lower() in MAP_BODY_SUFFIXES:
                _issue(result, "map_body_file_in_sealed_case", str(relative), "binary or rendered map-body files are forbidden")
            if stage in {"preregistered", "evidence_collection"} and (
                "build" in relative.parts or "figures" in relative.parts or path.name.startswith("boundary-hypotheses")
            ):
                _issue(result, "premature_reconstruction_artifact", str(relative), "sealed prospective case cannot contain reconstruction outputs")
    elif stage == "evaluation_opened":
        if held_out.get("isolation_state") != "evaluation_opened":
            _issue(result, "held_out_state_mismatch", "held-out-map-register.isolation_state", "evaluation_opened stage requires a matching register state")
        primary = held_out.get("candidates", [{}])[0]
        if primary.get("content_access_status") != "viewed" or primary.get("body_viewed") is not True:
            _issue(result, "missing_primary_content_access", "held-out-map-register.candidates[0]", "primary map body access must be recorded")

    if freeze.get("hash_algorithm") != "sha256":
        _issue(result, "unsupported_freeze_hash", "preregistration-freeze.hash_algorithm", "expected sha256")
    for index, artifact in enumerate(freeze.get("frozen_artifacts", [])):
        relative = artifact.get("path")
        path = _safe_file(case_dir, relative) if isinstance(relative, str) else None
        if path is None or not path.is_file():
            _issue(result, "missing_frozen_artifact", f"preregistration-freeze.frozen_artifacts[{index}]", str(relative))
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != artifact.get("sha256"):
            _issue(result, "freeze_hash_mismatch", str(relative), f"expected {artifact.get('sha256')}, got {actual}")

    lifecycle_path = case_dir / "lifecycle.json"
    try:
        lifecycle = load_json(lifecycle_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _issue(result, "missing_or_invalid_lifecycle", "lifecycle.json", str(exc))
        return result
    result.errors.extend(validate_schema(lifecycle, LIFECYCLE_SCHEMA))
    if result.errors:
        return result
    if lifecycle.get("case_id") != case_id:
        _issue(result, "case_id_mismatch", "lifecycle.json", f"expected {case_id!r}")
    lifecycle_text = _canonical_text(lifecycle)
    for token in held_out_tokens:
        if token in lifecycle_text:
            _issue(result, "held_out_reference_leak", "lifecycle.json", token)

    baseline = lifecycle["baseline"]
    freeze_commit = baseline["freeze_commit"]
    expected_baseline_hash = _baseline_state_sha256(str(case_id), freeze_commit, freeze)
    if baseline.get("state_sha256") != expected_baseline_hash:
        _issue(result, "baseline_state_hash_mismatch", "lifecycle.baseline.state_sha256", f"expected {expected_baseline_hash}")
    if baseline.get("stage") != case.get("research_stage") or baseline.get("reconstruction_ready") != case.get("reconstruction_ready"):
        _issue(result, "baseline_state_mismatch", "lifecycle.baseline", "must reproduce the frozen case shell")
    manifest_path = _safe_file(case_dir, baseline.get("freeze_manifest_path", ""))
    if manifest_path != (case_dir / str(case.get("freeze_manifest_path"))).resolve():
        _issue(result, "baseline_manifest_mismatch", "lifecycle.baseline.freeze_manifest_path", "must reference the frozen manifest")
    elif baseline.get("freeze_manifest_sha256") != _sha256_bytes(manifest_path.read_bytes()):
        _issue(result, "baseline_manifest_hash_mismatch", "lifecycle.baseline.freeze_manifest_sha256", "manifest hash changed")

    current_stage = str(case.get("research_stage"))
    previous_state_hash = expected_baseline_hash
    known_gap_ids = {gap.get("gap_id") for gap in bundle.get("evidence_gaps", [])}
    baseline_source_ids = {source.get("source_id") for source in bundle.get("sources", [])}
    seen_source_ids = set(baseline_source_ids)
    admitted_source_ids: set[str] = set()
    seen_observation_ids = {item.get("observation_id") for item in bundle.get("observations", [])}
    seen_claim_ids = {item.get("claim_id") for item in bundle.get("claims", [])}
    seen_decision_ids = {item.get("decision_id") for item in bundle.get("model_decisions", [])}
    gap_statuses = {gap.get("gap_id"): gap.get("status") for gap in bundle.get("evidence_gaps", [])}
    cumulative = {
        "queries": 0,
        "content_record_checks": 0,
        "sources_admitted": 0,
        "per_gap_follow_ups": {gap_id: 0 for gap_id in known_gap_ids},
    }
    round_ids: set[str] = set()
    terminal_seen = False
    registered_dirs: set[Path] = set()
    for index, entry in enumerate(lifecycle["rounds"]):
        entry_prefix = f"lifecycle.rounds[{index}]"
        round_id = entry["round_id"]
        if round_id in round_ids:
            _issue(result, "duplicate_round_id", entry_prefix, round_id)
        round_ids.add(round_id)
        if terminal_seen:
            _issue(result, "round_after_terminal_state", entry_prefix, round_id)
        expected_relative = f"research/rounds/{round_id}"
        if entry.get("path") != expected_relative:
            _issue(result, "invalid_round_path", f"{entry_prefix}.path", f"expected {expected_relative}")
        round_dir = _safe_file(case_dir, entry.get("path", ""))
        if round_dir is None or not round_dir.is_dir():
            _issue(result, "missing_round_directory", f"{entry_prefix}.path", str(entry.get("path")))
            continue
        registered_dirs.add(round_dir)
        manifest_file = round_dir / "round-manifest.json"
        if entry.get("manifest_path") != f"{expected_relative}/round-manifest.json":
            _issue(result, "invalid_round_manifest_path", f"{entry_prefix}.manifest_path", str(entry.get("manifest_path")))
        try:
            manifest = load_json(manifest_file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            _issue(result, "missing_or_invalid_round_manifest", str(manifest_file), str(exc))
            continue
        manifest_text = _canonical_text(manifest)
        for token in held_out_tokens:
            if token in manifest_text:
                _issue(result, "held_out_reference_leak", str(manifest_file.relative_to(case_dir)), token)
        manifest_hash = _sha256_bytes(manifest_file.read_bytes())
        if entry.get("manifest_sha256") != manifest_hash:
            _issue(result, "round_manifest_hash_mismatch", str(manifest_file.relative_to(case_dir)), f"expected {entry.get('manifest_sha256')}, got {manifest_hash}")
        if entry.get("previous_state_sha256") != previous_state_hash or manifest.get("previous_state_sha256") != previous_state_hash:
            _issue(result, "round_chain_mismatch", entry_prefix, f"expected previous state {previous_state_hash}")
        if manifest.get("round_id") != round_id or manifest.get("case_id") != case_id:
            _issue(result, "round_manifest_identity_mismatch", str(manifest_file.relative_to(case_dir)), round_id)
        manifest_names = {item.get("path") for item in manifest.get("files", [])}
        actual_names = {path.name for path in round_dir.iterdir() if path.is_file() and path.name != "round-manifest.json"}
        if manifest_names != ROUND_FILES or actual_names != ROUND_FILES:
            _issue(result, "round_file_set_mismatch", str(round_dir.relative_to(case_dir)), f"expected {sorted(ROUND_FILES)}")
        for file_entry in manifest.get("files", []):
            file_path = round_dir / str(file_entry.get("path", ""))
            if not file_path.is_file():
                _issue(result, "missing_round_file", str(file_path.relative_to(case_dir)), "registered file is absent")
                continue
            actual = _sha256_bytes(file_path.read_bytes())
            if actual != file_entry.get("sha256"):
                _issue(result, "round_file_hash_mismatch", str(file_path.relative_to(case_dir)), f"expected {file_entry.get('sha256')}, got {actual}")
        documents = _load_round_files(round_dir, result)
        if len(documents) != len(ROUND_FILES):
            previous_state_hash = manifest_hash
            continue
        for name, document in documents.items():
            if document.get("case_id") != case_id or document.get("round_id") != round_id:
                _issue(result, "round_document_identity_mismatch", f"{expected_relative}/{name}", round_id)
            text = _canonical_text(document)
            for token in held_out_tokens:
                if token in text:
                    _issue(result, "held_out_reference_leak", f"{expected_relative}/{name}", token)

        round_meta = documents["round.json"]
        if round_meta.get("previous_state_sha256") != previous_state_hash:
            _issue(result, "round_chain_mismatch", f"{expected_relative}/round.json:previous_state_sha256", f"expected {previous_state_hash}")
        first_access = round_meta.get("first_content_access", {})
        if first_access.get("preregistration_commit") != freeze_commit:
            _issue(result, "first_access_freeze_mismatch", f"{expected_relative}/round.json:first_content_access", freeze_commit)
        for flag in ("held_out_content_accessed", "historical_territorial_map_body_accessed"):
            if first_access.get(flag) is not False:
                _issue(result, "held_out_content_accessed", f"{expected_relative}/round.json:first_content_access.{flag}", "must be false")
        transition = round_meta.get("transition", {})
        if transition.get("from") != current_stage or transition.get("to") not in ALLOWED_TRANSITIONS.get(current_stage, frozenset()):
            _issue(result, "invalid_lifecycle_transition", f"{expected_relative}/round.json:transition", f"{current_stage} -> {transition.get('to')}")
        current_stage = str(transition.get("to"))
        terminal_seen = current_stage in TERMINAL_STAGES
        if round_meta.get("review_status") != "reviewed":
            _issue(result, "unreviewed_round", f"{expected_relative}/round.json", "only reviewed rounds determine effective state")

        round_state = _validate_source_round(
            documents,
            baseline_source_ids,
            known_gap_ids,
            seen_source_ids,
            admitted_source_ids,
            seen_observation_ids,
            seen_claim_ids,
            seen_decision_ids,
            result,
            expected_relative,
        )
        for key in ("queries", "content_record_checks", "sources_admitted"):
            cumulative[key] += round_state[key]
        for gap_id, count in round_state["per_gap_follow_ups"].items():
            cumulative["per_gap_follow_ups"][gap_id] += count
        for update in round_state["gap_updates"]:
            gap_statuses[update["gap_id"]] = update["status"]
        gate = documents["gate.json"]
        if terminal_seen:
            if transition.get("terminal_outcome") != "completed_no_reconstruction" or transition.get("reconstruction_ready") is not False:
                _issue(result, "invalid_terminal_outcome", f"{expected_relative}/round.json", "terminal state must record completed_no_reconstruction and readiness false")
            if gate.get("overall_passed") is not False or gate.get("decision") != "completed_no_reconstruction":
                _issue(result, "gate_outcome_mismatch", f"{expected_relative}/gate.json", "failed gate must terminate without reconstruction")
        previous_state_hash = manifest_hash

    rounds_root = case_dir / "research" / "rounds"
    actual_dirs = {path.resolve() for path in rounds_root.iterdir() if path.is_dir()} if rounds_root.is_dir() else set()
    if actual_dirs != registered_dirs:
        difference = sorted(str(path.relative_to(case_dir)) for path in actual_dirs ^ registered_dirs)
        _issue(result, "unregistered_or_missing_round", "research/rounds", str(difference))

    limits = prereg.get("search_budget", {})
    for consumed_key, limit_key in (
        ("queries", "query_limit"),
        ("content_record_checks", "content_record_limit"),
        ("sources_admitted", "source_admission_limit"),
    ):
        if cumulative[consumed_key] > limits.get(limit_key, -1):
            _issue(result, "research_budget_exceeded", f"lifecycle.effective_state.budget_consumed.{consumed_key}", f"{cumulative[consumed_key]} > {limits.get(limit_key)}")
    for gap_id, count in cumulative["per_gap_follow_ups"].items():
        if count > limits.get("per_gap_follow_up_limit", -1):
            _issue(result, "research_budget_exceeded", f"lifecycle.effective_state.budget_consumed.per_gap_follow_ups.{gap_id}", f"{count} > {limits.get('per_gap_follow_up_limit')}")

    effective = lifecycle["effective_state"]
    expected_effective = {
        "stage": current_stage,
        "reconstruction_ready": current_stage == "reconstructed_pre_evaluation",
        "terminal_outcome": "completed_no_reconstruction" if current_stage == "completed_no_reconstruction" else None,
        "reviewed_round_ids": [entry["round_id"] for entry in lifecycle["rounds"]],
        "gap_statuses": [{"gap_id": gap_id, "status": gap_statuses[gap_id]} for gap_id in sorted(gap_statuses)],
        "budget_consumed": cumulative,
        "held_out_isolation": "metadata_only_unviewed" if current_stage != "evaluation_opened" else "evaluation_opened",
    }
    if effective != expected_effective:
        _issue(result, "effective_state_mismatch", "lifecycle.effective_state", "must equal the frozen baseline plus reviewed round deltas")

    return result


__all__ = [
    "validate_held_out_register",
    "validate_preregistration",
    "validate_prospective_case",
    "effective_prospective_state",
    "astronomical_year_from_bce",
]
