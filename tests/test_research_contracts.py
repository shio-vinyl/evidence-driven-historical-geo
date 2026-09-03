from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from historical_geo.research_contracts import (
    validate_research_bundle,
    validate_schema,
    validate_search_targets,
    validate_uncertainty_diagnosis,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def codes(result) -> set[str]:
    return {issue.code for issue in result.errors}


def bundle() -> dict:
    return {
        "contract_version": "historical_geo.research_bundle.v0.2",
        "case_id": "test-case",
        "sources": [
            {
                "source_id": "SRC_RESEARCH",
                "title": "Reviewed chronicle",
                "source_type": "book",
                "rights_status": "citation permitted",
                "redistribution": "citation_only",
                "use_role": "research",
            },
            {
                "source_id": "SRC_EVALUATION",
                "title": "Comparison atlas",
                "source_type": "map",
                "rights_status": "comparison only",
                "redistribution": "citation_only",
                "use_role": "evaluation_only",
            },
        ],
        "observations": [
            {
                "observation_id": "OBS_CONTROL",
                "source_id": "SRC_RESEARCH",
                "locator": "p. 12",
                "paraphrase": "The city was held by the named polity.",
                "verification_status": "checked against the cited page",
                "data": {"coordinates": [35.2, 31.8], "feature_id": "city-1"},
            },
            {
                "observation_id": "OBS_COUNTER",
                "source_id": "SRC_RESEARCH",
                "locator": "p. 27",
                "paraphrase": "A later account disputes continuous control.",
                "verification_status": "checked against the cited page",
            },
        ],
        "claims": [
            {
                "claim_id": "CLM_CONTROL",
                "supporting_observation_ids": ["OBS_CONTROL"],
                "challenging_observation_ids": [],
                "semantic_role": "control_point",
                "status": "supported",
                "rationale": "The observation supports a point anchor only.",
                "statement": "The named polity controlled the city.",
                "entity": "Test polity",
                "slice": 1130,
                "temporal_scope": {"kind": "year", "value": 1130},
                "spatial_scope": {"kind": "point", "feature_id": "city-1"},
            },
            {
                "claim_id": "CLM_DISPUTED",
                "supporting_observation_ids": ["OBS_CONTROL"],
                "challenging_observation_ids": ["OBS_COUNTER"],
                "semantic_role": "spatial_extent",
                "status": "disputed",
                "rationale": "The accounts conflict over the surrounding territory.",
                "statement": "The polity controlled the surrounding territory.",
                "entity": "Test polity",
                "slice": 1130,
            },
        ],
        "model_decisions": [
            {
                "decision_id": "DEC_CONTROL",
                "role": "control_point",
                "review_status": "admitted",
                "supporting_claim_ids": ["CLM_CONTROL"],
                "challenging_claim_ids": [],
                "source_ids": ["SRC_RESEARCH"],
                "rationale": "Use the supported claim as a backend-neutral control point.",
                "parameters": {"feature_id": "city-1"},
            },
            {
                "decision_id": "DEC_ASSUMPTION",
                "role": "spatial_constraint",
                "review_status": "assumption",
                "supporting_claim_ids": [],
                "challenging_claim_ids": ["CLM_DISPUTED"],
                "source_ids": [],
                "rationale": "A bounded scenario needs an explicit spatial constraint.",
                "assumption_reason": "No reviewed source settles the extent at this slice.",
                "parameters": {"constraint": "bounded extent"},
            },
        ],
        "evidence_gaps": [
            {
                "gap_id": "GAP_EXTENT",
                "cause": "conflicting_evidence",
                "status": "open",
                "question": "Which settlements delimit control in the disputed area?",
                "success_criteria": "Locate independently reviewable statements for named settlements.",
                "stop_condition": "Stop when two directly relevant sources remain irreconcilable.",
                "preferred_source_types": ["primary chronicle", "regional study"],
                "related_claim_ids": ["CLM_DISPUTED"],
                "related_decision_ids": ["DEC_ASSUMPTION"],
            }
        ],
    }


def diagnosis() -> dict:
    return {
        "contract_version": "historical_geo.uncertainty_diagnosis.v0.2",
        "case_id": "test-case",
        "baseline_scenario": "reviewed-baseline",
        "slices": [
            {
                "slice": 1130,
                "classification": "mixed",
                "affected_grid_cells": {"evidence": 4, "model": 6, "total": 8},
                "changed_scenarios": {"evidence": ["inclusive"], "model": ["projection-normal"]},
                "changed_decision_ids": {
                    "evidence": ["DEC_CONTROL"],
                    "model": ["DEC_ASSUMPTION"],
                    "all": ["DEC_ASSUMPTION", "DEC_CONTROL"],
                },
            }
        ],
    }


def targets() -> dict:
    return {
        "contract_version": "historical_geo.search_targets.v0.2",
        "case_id": "test-case",
        "targets": [
            {
                "target_id": "TARGET_EXTENT",
                "evidence_gap_ids": ["GAP_EXTENT"],
                "claim_ids": ["CLM_DISPUTED"],
                "decision_ids": ["DEC_ASSUMPTION"],
                "question": "Which source names control of the relevant settlements?",
                "preferred_source_types": ["primary chronicle", "regional study"],
                "success_criteria": "A locatable paraphrase about control at the target slice.",
                "stop_condition": "Stop after the gap success criterion is met or suitable sources are exhausted.",
                "priority_basis": {
                    "affected_grid_cells": 4,
                    "related_decision_count": 1,
                    "related_decision_ids": ["DEC_ASSUMPTION"],
                    "slices": [1130],
                },
                "status": "open",
            }
        ],
    }


def test_valid_bundle_preserves_four_layers_and_evidence_gaps() -> None:
    assert validate_research_bundle(bundle()).ok


def test_observation_requires_locator_paraphrase_and_verification_status() -> None:
    data = bundle()
    assert data["observations"][0]["data"]["feature_id"] == "city-1"
    del data["observations"][0]["locator"]
    result = validate_research_bundle(data)
    assert "schema_error" in codes(result)


def test_claim_context_and_decision_parameters_are_required() -> None:
    data = bundle()
    del data["claims"][0]["statement"]
    assert "schema_error" in codes(validate_research_bundle(data))

    data = bundle()
    del data["model_decisions"][0]["parameters"]
    assert "schema_error" in codes(validate_research_bundle(data))


def test_claim_confidence_is_rejected_instead_of_accepting_false_precision() -> None:
    data = bundle()
    data["claims"][0]["confidence"] = 0.8
    result = validate_research_bundle(data)
    assert "schema_error" in codes(result)


def test_evaluation_only_source_cannot_create_an_observation_or_claim() -> None:
    data = bundle()
    data["observations"][0]["source_id"] = "SRC_EVALUATION"
    result = validate_research_bundle(data)
    assert "evaluation_only_source_used_for_research" in codes(result)


def test_evaluation_only_source_cannot_support_model_decision() -> None:
    data = bundle()
    data["model_decisions"][0]["source_ids"] = ["SRC_EVALUATION"]
    result = validate_research_bundle(data)
    assert "evaluation_only_source_used_for_research" in codes(result)


def test_claim_reference_and_status_semantics_are_checked() -> None:
    data = bundle()
    data["claims"][0]["supporting_observation_ids"] = ["OBS_MISSING"]
    result = validate_research_bundle(data)
    assert "missing_observation" in codes(result)

    data = bundle()
    data["claims"][1]["challenging_observation_ids"] = []
    result = validate_research_bundle(data)
    assert "schema_error" in codes(result)


def test_admitted_decision_must_have_supported_claim_and_assumptions_need_reason() -> None:
    data = bundle()
    data["model_decisions"][0]["supporting_claim_ids"] = ["CLM_DISPUTED"]
    result = validate_research_bundle(data)
    assert "admitted_decision_uses_non_supported_claim" in codes(result)

    data = bundle()
    del data["model_decisions"][1]["assumption_reason"]
    result = validate_research_bundle(data)
    assert "schema_error" in codes(result)


def test_gap_references_are_checked() -> None:
    data = bundle()
    data["evidence_gaps"][0]["related_decision_ids"] = ["DEC_MISSING"]
    result = validate_research_bundle(data)
    assert "missing_decision" in codes(result)


def test_independent_diagnosis_and_search_targets_resolve_bundle_references() -> None:
    data = bundle()
    assert validate_uncertainty_diagnosis(diagnosis(), data).ok
    assert validate_search_targets(targets(), data).ok

    bad_diagnosis = diagnosis()
    bad_diagnosis["slices"][0]["changed_decision_ids"]["all"] = ["DEC_MISSING"]
    assert "missing_decision" in codes(validate_uncertainty_diagnosis(bad_diagnosis, data))

    bad_targets = deepcopy(targets())
    bad_targets["targets"][0]["claim_ids"] = ["CLM_MISSING"]
    assert "missing_claim" in codes(validate_search_targets(bad_targets, data))


def test_v02_schemas_are_valid_draft_2020_12() -> None:
    from jsonschema import Draft202012Validator

    for name in ("research-bundle.schema.json", "uncertainty-diagnosis.schema.json", "search-targets.schema.json"):
        Draft202012Validator.check_schema(json.loads((SCHEMAS / name).read_text()))


def test_standalone_schema_validation_is_available() -> None:
    assert not validate_schema(bundle(), SCHEMAS / "research-bundle.schema.json")
