from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from historical_geo.preflight import (
    BUDGET_LIMITS,
    REVIEW_GATES,
    assess_source_structure_preflight,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/research/prospective-source-structure-preflight.json"


def _audit() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def _synthetic_candidate(candidate_id: str) -> dict:
    """Explicitly constructed gate fixture, never historical source evidence."""
    sources = [
        {"source_id": f"S{i}", "lineage_id": f"L{i}", "rights": "synthetic",
         "evidence_role": "political_archive_record", "independence_verified": True}
        for i in range(6)
    ]
    return {
        "candidate_id": candidate_id,
        "centers": [{"entity_id": f"C{i}", "center_verified": True} for i in range(2)],
        "query_log": [{"query_id": "Q1", "kind": "research"},
                      {"query_id": "Q2", "kind": "held_out_metadata"}],
        "preliminary_sources": sources,
        "content_record_check_log": [
            {"check_id": f"K{i}", "source_id": source["source_id"],
             "result": "full_text", "lawful_access_verified": True, "map_body_selected": False}
            for i, source in enumerate(sources)
        ],
        "source_matrix": [
            {"row_id": f"R{center}-{sender}-{place}", "entity": f"C{center}",
             "locality": f"P{place}", "source_id": f"S{sender}",
             "source_lineage": f"L{sender}", "rights": "synthetic",
             "political_relation": True, "content_observed": True,
             "temporal_applicability": "candidate_phase"}
            for center in range(2) for sender in range(2) for place in range(4)
        ],
        "locality_register": [
            {"locality_id": f"P{i}", "identification_verified": True,
             "source_id": "S5", "locator": f"synthetic record {i}"}
            for i in range(12)
        ],
        "conflicts_or_exclusions": [
            {"exclusion_id": "X1", "row_ids": ["R0-0-0"]},
            {"exclusion_id": "X2", "row_ids": ["R1-1-1"]},
        ],
        "held_out_candidates": [
            {"reference_id": "H1", "metadata_only": True, "excluded": False,
             "contamination": False, "ten_unit_expectation_supported": True},
        ],
        "isolation_review": {"status": "pass"},
        "review_gates": {key: {"status": "pass", "rationale": "synthetic fixture"}
                         for key in REVIEW_GATES},
    }


def _synthetic() -> dict:
    return {"limits": dict(BUDGET_LIMITS), "preferred_if_both_pass": "A",
            "candidates": [_synthetic_candidate("A"), _synthetic_candidate("B")]}


def _first_result(document: dict) -> dict:
    return assess_source_structure_preflight(document)["candidates"]["A"]


def test_checked_audit_recomputes_to_no_go_without_a_fourth_case() -> None:
    audit = _audit()
    assert assess_source_structure_preflight(audit) == audit["assessment"]
    assert audit["assessment"]["selected_candidate_id"] is None
    assert audit["assessment"]["decision"] == "NO-GO"
    assert audit["question_freeze"] is None
    assert audit["preregistration_created"] is False
    for name in ("amarna_northern_canaan", "florence_siena_contado"):
        assert not (ROOT / "cases" / name).exists()
    for name in ("mercia_welsh_frontier", "sennacherib_701_southern_levant"):
        case = ROOT / "cases" / name / "public"
        state = json.loads((case / "lifecycle.json").read_text())["effective_state"]
        assert state["stage"] == "completed_no_reconstruction"
        assert state["held_out_isolation"] == "metadata_only_unviewed"


def test_checked_audit_retains_actual_failures_overruns_and_unverified_gates() -> None:
    audit = _audit()
    a, b = list(audit["assessment"]["candidates"].values())
    assert a["full_text_access"] == {"numerator": 1, "denominator": 6}
    assert b["full_text_access"] == {"numerator": 3, "denominator": 6}
    assert a["budget_consumed"]["queries"] == b["budget_consumed"]["queries"] == 9
    assert b["budget_consumed"]["held_out_candidates"] == 3
    assert len(audit["protocol_deviations"]) == 4
    for candidate in (a, b):
        assert not candidate["gates"]["two_independent_lineages_per_center"]
        assert not candidate["gates"]["stable_temporal_phase"]
        assert not candidate["gates"]["comparator_ten_units"]


@pytest.mark.parametrize("a_pass,b_pass,selected", [
    (True, True, "A"), (True, False, "A"), (False, True, "B"), (False, False, None),
])
def test_selection_uses_computed_gates_not_a_declared_go(a_pass, b_pass, selected) -> None:
    document = _synthetic()
    for candidate, passed in zip(document["candidates"], (a_pass, b_pass)):
        candidate["decision"] = "GO"  # Untrusted summary must have no effect.
        if not passed:
            candidate["review_gates"].pop("stable_temporal_phase")
    assert assess_source_structure_preflight(document)["selected_candidate_id"] == selected


def test_metadata_queries_are_not_free_extra_queries() -> None:
    document = _synthetic()
    candidate = document["candidates"][0]
    candidate["query_log"] = [{"query_id": f"Q{i}", "kind": "research"} for i in range(8)]
    candidate["query_log"].append({"query_id": "HQ1", "kind": "held_out_metadata"})
    assert _first_result(document)["gates"]["budget_compliant"] is False
    candidate["query_log"].pop(0)
    assert _first_result(document)["gates"]["budget_compliant"] is True


def test_legal_access_uses_distinct_sources_and_does_not_count_snippets() -> None:
    document = _synthetic()
    checks = document["candidates"][0]["content_record_check_log"]
    checks[0]["result"] = "search_indexed_line_text"
    assert _first_result(document)["gates"]["legal_text_access_70_percent"] is True  # 5/6
    checks[1]["result"] = "catalog_only"
    assert _first_result(document)["gates"]["legal_text_access_70_percent"] is False  # 4/6
    checks[1]["result"] = "full_text"
    checks[1]["source_id"] = checks[2]["source_id"]
    assert _first_result(document)["full_text_access"]["numerator"] == 4


def test_repeated_sender_or_translation_cannot_add_a_political_lineage() -> None:
    document = _synthetic()
    candidate = document["candidates"][0]
    candidate["preliminary_sources"][1]["lineage_id"] = "L0"
    for row in candidate["source_matrix"]:
        if row["source_id"] == "S1":
            row["source_lineage"] = "L0"
    result = _first_result(document)
    assert result["independent_political_lineages_per_center"] == {"C0": ["L0"], "C1": ["L0"]}
    assert result["gates"]["two_independent_lineages_per_center"] is False


@pytest.mark.parametrize("role", ["gazetteer", "occupation_archaeology", "finding_aid", "corpus_metadata"])
def test_nonpolitical_source_cannot_supply_missing_independence(role: str) -> None:
    document = _synthetic()
    document["candidates"][0]["preliminary_sources"][1]["evidence_role"] = role
    assert _first_result(document)["gates"]["two_independent_lineages_per_center"] is False


@pytest.mark.parametrize("field,value", [
    ("temporal_applicability", "sons_phase_unresolved"), ("content_observed", False),
    ("political_relation", False),
])
def test_unchecked_or_out_of_phase_rows_cannot_supply_lineages(field, value) -> None:
    document = _synthetic()
    for row in document["candidates"][0]["source_matrix"]:
        if row["source_id"] == "S1":
            row[field] = value
    assert _first_result(document)["gates"]["two_independent_lineages_per_center"] is False


@pytest.mark.parametrize("field,value", [
    ("metadata_only", False), ("excluded", True), ("contamination", True),
    ("ten_unit_expectation_supported", False),
])
def test_contaminated_or_unsubstantiated_comparator_cannot_pass(field, value) -> None:
    document = _synthetic()
    document["candidates"][0]["held_out_candidates"][0][field] = value
    assert _first_result(document)["gates"]["comparator_ten_units"] is False


def test_mismatched_matrix_lineage_or_unknown_source_is_rejected() -> None:
    document = _synthetic()
    document["candidates"][0]["source_matrix"][0]["source_lineage"] = "invented"
    with pytest.raises(ValueError, match="lineage and rights"):
        assess_source_structure_preflight(document)
    document = _synthetic()
    document["candidates"][0]["source_matrix"][0]["source_id"] = "unknown"
    with pytest.raises(ValueError, match="unknown source"):
        assess_source_structure_preflight(document)


def test_limits_cannot_be_rewritten_to_hide_an_overrun() -> None:
    document = _synthetic()
    document["limits"]["queries"] = 9
    with pytest.raises(ValueError, match="limits cannot"):
        assess_source_structure_preflight(document)


def test_access_flag_cannot_be_overridden_by_a_clean_isolation_summary() -> None:
    document = _synthetic()
    document["candidates"][0]["content_record_check_log"][0]["map_body_selected"] = True
    result = _first_result(document)
    assert result["gates"]["isolation_review"] is False
    assert result["decision"] == "NO-GO"


def test_assessment_does_not_mutate_the_ledger() -> None:
    document = _audit()
    before = deepcopy(document)
    assess_source_structure_preflight(document)
    assert document == before
