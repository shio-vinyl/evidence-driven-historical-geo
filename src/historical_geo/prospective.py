"""Validation gates for prospective cases before held-out material is opened."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
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
SEALED_STAGES = frozenset({"preregistered", "evidence_collection", "reconstructed_pre_evaluation"})
MAP_BODY_SUFFIXES = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".svg"})


def _issue(result: ValidationResult, code: str, path: str, message: str) -> None:
    result.errors.append(ContractIssue(code, path, message))


def _load(case_dir: Path, case: Mapping[str, Any], field: str) -> dict[str, Any]:
    return load_json(case_dir / str(case[field]))


def _canonical_text(document: Any) -> str:
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _safe_file(case_dir: Path, relative: str) -> Path | None:
    path = Path(relative)
    if path.is_absolute():
        return None
    resolved = (case_dir / path).resolve()
    return resolved if case_dir == resolved or case_dir in resolved.parents else None


def validate_preregistration(document: Mapping[str, Any]) -> ValidationResult:
    result = ValidationResult()
    result.errors.extend(validate_schema(document, PREREGISTRATION_SCHEMA))
    return result


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

    return result


__all__ = [
    "validate_held_out_register",
    "validate_preregistration",
    "validate_prospective_case",
]
