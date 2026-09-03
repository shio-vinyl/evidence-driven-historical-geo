from __future__ import annotations

import json
from pathlib import Path

import pytest

from historical_geo.cli import main
from historical_geo.search_policy_experiment import (
    PolicyExperimentError,
    RESULT_SCHEMA,
    _schema_errors,
    run_policy_experiment,
    run_policy_experiment_files,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_EXPERIMENT = (
    ROOT
    / "cases"
    / "crusader_states"
    / "public"
    / "research"
    / "experiments"
    / "equal-budget-policy"
)


def targets() -> dict:
    return {
        "case_id": "test-case",
        "targets": [
            {
                "target_id": "TARGET_A",
                "status": "open",
                "evidence_gap_ids": ["GAP_A"],
                "priority_basis": {"affected_grid_cells": 10},
            },
            {
                "target_id": "TARGET_B",
                "status": "open",
                "evidence_gap_ids": ["GAP_B"],
                "priority_basis": {"affected_grid_cells": 8},
            },
            {
                "target_id": "TARGET_C",
                "status": "open",
                "evidence_gap_ids": ["GAP_C"],
                "priority_basis": {"affected_grid_cells": 1},
            },
        ],
    }


def config() -> dict:
    return {
        "contract_version": "historical_geo.search_policy_experiment.v0.1",
        "case_id": "test-case",
        "evaluation_mode": "deterministic_replay_with_constructed_outcomes",
        "evidence_budget": 2,
        "search_targets_path": "targets.json",
        "initial_evidence_sensitive_cell_ranges": [
            {"slice": 1, "start": 0, "end_exclusive": 10}
        ],
        "policies": [
            {
                "policy_id": "targeted",
                "selection": "descending_spatial_priority",
                "selection_rationale": "Use declared spatial priority.",
            },
            {
                "policy_id": "fixed",
                "selection": "declared_order_without_spatial_feedback",
                "target_order": ["TARGET_C", "TARGET_B", "TARGET_A"],
                "selection_rationale": "Stable non-spatial order.",
            },
            {
                "policy_id": "broad",
                "selection": "declared_order_without_spatial_feedback",
                "target_order": ["TARGET_B", "TARGET_A", "TARGET_C"],
                "selection_rationale": "Broad-reading order.",
            },
        ],
        "fixture_outcomes": [
            {
                "target_id": "TARGET_A",
                "outcome_kind": "constructed_fixture",
                "closed_gap_ids": ["GAP_A"],
                "affected_cell_ranges": [{"slice": 1, "start": 0, "end_exclusive": 5}],
                "resolved_sensitive_cell_ranges": [{"slice": 1, "start": 0, "end_exclusive": 3}],
                "fixture_note": "Constructed positive outcome.",
            },
            {
                "target_id": "TARGET_B",
                "outcome_kind": "constructed_fixture",
                "closed_gap_ids": [],
                "affected_cell_ranges": [{"slice": 1, "start": 3, "end_exclusive": 8}],
                "resolved_sensitive_cell_ranges": [{"slice": 1, "start": 3, "end_exclusive": 5}],
                "fixture_note": "Constructed inconclusive outcome.",
            },
            {
                "target_id": "TARGET_C",
                "outcome_kind": "constructed_fixture",
                "closed_gap_ids": ["GAP_C"],
                "affected_cell_ranges": [{"slice": 1, "start": 8, "end_exclusive": 10}],
                "resolved_sensitive_cell_ranges": [{"slice": 1, "start": 8, "end_exclusive": 10}],
                "fixture_note": "Constructed positive outcome.",
            },
        ],
        "limitations": ["All outcomes are constructed."],
    }


def result_by_policy(result: dict) -> dict[str, dict]:
    return {row["policy_id"]: row for row in result["policy_results"]}


def test_equal_budget_replay_counts_unique_cells_and_only_three_metrics() -> None:
    result = run_policy_experiment(config(), targets())
    rows = result_by_policy(result)

    assert {row["retrievals"] and len(row["retrievals"]) for row in rows.values()} == {2}
    assert rows["targeted"]["selected_target_ids"] == ["TARGET_A", "TARGET_B"]
    assert rows["targeted"]["metrics"] == {
        "gaps_closed_per_retrieval": 0.5,
        "new_evidence_affected_grid_cells": 8,
        "remaining_evidence_sensitive_cells": 5,
    }
    assert set(rows["fixed"]["metrics"]) == {
        "gaps_closed_per_retrieval",
        "new_evidence_affected_grid_cells",
        "remaining_evidence_sensitive_cells",
    }


def test_declared_baselines_must_offer_the_same_target_pool() -> None:
    data = config()
    data["policies"][1]["target_order"] = ["TARGET_A", "TARGET_B"]
    with pytest.raises(PolicyExperimentError, match="permutation of every open target"):
        run_policy_experiment(data, targets())


def test_fixture_cannot_resolve_cells_it_did_not_affect() -> None:
    data = config()
    data["fixture_outcomes"][0]["resolved_sensitive_cell_ranges"] = [
        {"slice": 1, "start": 5, "end_exclusive": 6}
    ]
    with pytest.raises(PolicyExperimentError, match="resolves cells it does not affect"):
        run_policy_experiment(data, targets())


def test_fixture_cannot_claim_a_gap_outside_its_real_search_target() -> None:
    data = config()
    data["fixture_outcomes"][0]["closed_gap_ids"] = ["GAP_B"]
    with pytest.raises(PolicyExperimentError, match="outside its search target"):
        run_policy_experiment(data, targets())


def test_checked_in_public_result_is_schema_valid_and_exactly_reproducible() -> None:
    expected = json.loads((PUBLIC_EXPERIMENT / "result.json").read_text(encoding="utf-8"))
    actual = run_policy_experiment_files(PUBLIC_EXPERIMENT / "experiment.json")

    assert actual == expected
    assert _schema_errors(actual, RESULT_SCHEMA) == []
    assert actual["evaluation_mode"] == "deterministic_replay_with_constructed_outcomes"


def test_cli_replays_policy_experiment_and_can_write_result(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    assert main([
        "policy-experiment",
        str(PUBLIC_EXPERIMENT / "experiment.json"),
        "--output",
        str(output),
    ]) == 0
    assert json.loads(output.read_text()) == run_policy_experiment_files(
        PUBLIC_EXPERIMENT / "experiment.json"
    )
