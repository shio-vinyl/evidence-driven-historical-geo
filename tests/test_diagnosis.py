from __future__ import annotations

import numpy as np
import pytest

from historical_geo.diagnosis import build_diagnosis_documents, diagnose_uncertainty
from historical_geo.research_contracts import validate_search_targets, validate_uncertainty_diagnosis


def config() -> dict:
    return {
        "baseline": "baseline",
        "scenarios": {
            "baseline": {"axis": "baseline"},
            "evidence-a": {
                "axis": "evidence",
                "changed_decision_ids": ["D_E1"],
            },
            "evidence-b": {
                "axis": "evidence",
                "changed_decision_ids": ["D_E2", "D_SHARED"],
            },
            "model-a": {
                "axis": "model",
                "changed_decision_ids": ["D_M1", "D_SHARED"],
            },
        },
    }


def gap(gap_id: str, decisions: list[str], status: str = "open") -> dict:
    return {
        "gap_id": gap_id,
        "status": status,
        "related_decision_ids": decisions,
        "question": f"Question for {gap_id}?",
        "preferred_source_types": ["dated charter", "critical edition"],
        "success_criteria": "A dated, place-specific observation resolves the decision.",
        "stop_condition": "Stop after the named corpus and catalogue are exhausted.",
    }


def test_diagnoses_each_changed_slice_and_attributes_decisions() -> None:
    assignments = {
        "1187": {
            "baseline": [[1, 1], [2, 2]],
            "evidence-a": [[1, 3], [2, 2]],
            "evidence-b": [[1, 1], [2, 2]],
            "model-a": [[1, 1], [4, 2]],
        },
        "1130": {
            "baseline": np.array([[1, 1], [2, 2]], dtype=np.int16),
            "evidence-a": np.array([[1, 1], [2, 2]], dtype=np.int16),
            "evidence-b": np.array([[1, 3], [4, 2]], dtype=np.int16),
            "model-a": np.array([[1, 1], [2, 2]], dtype=np.int16),
        },
    }

    result = diagnose_uncertainty(config(), assignments, [gap("G_E2", ["D_E2"])])

    assert [item["slice"] for item in result["slices"]] == ["1130", "1187"]
    evidence_only, mixed = result["slices"]
    assert evidence_only["classification"] == "evidence_gap"
    assert evidence_only["affected_grid_cells"] == {"evidence": 2, "model": 0, "total": 2}
    assert evidence_only["changed_decision_ids"] == {
        "evidence": ["D_E2", "D_SHARED"],
        "model": [],
        "all": ["D_E2", "D_SHARED"],
    }
    assert mixed["classification"] == "mixed"
    assert mixed["changed_decision_ids"]["evidence"] == ["D_E1"]
    assert mixed["changed_decision_ids"]["model"] == ["D_M1", "D_SHARED"]


def test_search_targets_use_open_evidence_gaps_and_transparent_count_priority() -> None:
    assignments = {
        1: {
            "baseline": [1, 1, 1, 1, 1],
            "evidence-a": [2, 2, 2, 1, 1],
            "evidence-b": [1, 1, 1, 2, 1],
            "model-a": [1, 1, 1, 1, 2],
        }
    }
    gaps = [
        gap("G_Z", ["D_E2", "D_SHARED"]),
        gap("G_B", ["D_E1"]),
        gap("G_A", ["D_E1"]),
        gap("G_CLOSED", ["D_E1"], status="closed"),
    ]

    result = diagnose_uncertainty(config(), assignments, gaps)

    # Three affected cells outrank one; output does not depend on input order.
    assert [target["gap_id"] for target in result["search_targets"]] == ["G_A", "G_B", "G_Z"]
    assert result["search_targets"][0]["priority_basis"] == {
        "affected_grid_cells": 3,
        "related_decision_count": 1,
        "related_decision_ids": ["D_E1"],
        "slices": [1],
    }
    assert result["search_targets"][2]["preferred_source_types"] == [
        "dated charter",
        "critical edition",
    ]


def test_builds_schema_valid_public_documents() -> None:
    cfg = config()
    cfg["case_id"] = "test-case"
    assignments = {
        1130: {
            "baseline": [1, 1, 1],
            "evidence-a": [2, 1, 1],
            "evidence-b": [1, 1, 1],
            "model-a": [1, 2, 1],
        }
    }
    item = gap("G_E1", ["D_E1"])
    item["related_claim_ids"] = ["C_E1"]

    diagnosis, targets = build_diagnosis_documents("test-case", cfg, assignments, [item])

    assert diagnosis["baseline_scenario"] == "baseline"
    assert targets["targets"][0]["target_id"] == "TARGET_G_E1"
    assert not validate_uncertainty_diagnosis(diagnosis).errors
    assert not validate_search_targets(targets).errors


def test_model_sensitivity_never_creates_historical_source_search() -> None:
    assignments = {
        "slice": {
            "baseline": [1, 1, 1],
            "evidence-a": [1, 1, 1],
            "evidence-b": [1, 1, 1],
            "model-a": [1, 2, 1],
        }
    }
    # D_SHARED is deliberately named on both axes.  With no observed evidence
    # scenario effect, even an open gap cannot trigger a search target.
    result = diagnose_uncertainty(config(), assignments, [gap("G_MODEL", ["D_SHARED", "D_M1"])])

    assert result["slices"][0]["classification"] == "model_sensitivity"
    assert result["search_targets"] == []


def test_mixed_slice_does_not_search_for_gap_linked_only_to_model_change() -> None:
    assignments = {
        "slice": {
            "baseline": [1, 1, 1],
            "evidence-a": [2, 1, 1],
            "evidence-b": [1, 1, 1],
            "model-a": [1, 2, 1],
        }
    }

    result = diagnose_uncertainty(config(), assignments, [gap("G_MODEL", ["D_M1"])])

    assert result["slices"][0]["classification"] == "mixed"
    assert result["search_targets"] == []


@pytest.mark.parametrize(
    "mutate, message",
    [
        (lambda cfg, data: cfg.update({"baseline": "missing"}), "does not match the declared baseline"),
        (
            lambda cfg, data: cfg["scenarios"]["evidence-a"].update({"changed_decision_ids": []}),
            "at least one changed decision ID",
        ),
        (lambda cfg, data: data["slice"].update({"evidence-a": [1, 2]}), "shape mismatch"),
        (lambda cfg, data: data["slice"].update({"model-a": [1.0, 1.0, 1.0]}), "only integers"),
    ],
)
def test_rejects_invalid_or_non_comparable_scenarios(mutate, message: str) -> None:
    cfg = config()
    assignments = {
        "slice": {
            "baseline": [1, 1, 1],
            "evidence-a": [1, 1, 1],
            "evidence-b": [1, 1, 1],
            "model-a": [1, 1, 1],
        }
    }
    mutate(cfg, assignments)

    with pytest.raises(ValueError, match=message):
        diagnose_uncertainty(cfg, assignments, [])


def test_omits_unchanged_slices_and_is_deterministic() -> None:
    assignments = {
        "slice": {
            "baseline": [[1, 1]],
            "evidence-a": [[1, 1]],
            "evidence-b": [[1, 1]],
            "model-a": [[1, 1]],
        }
    }

    first = diagnose_uncertainty(config(), assignments, [gap("G", ["D_E1"])])
    second = diagnose_uncertainty(config(), assignments, [gap("G", ["D_E1"])])

    assert first == second == {"slices": [], "search_targets": []}


def test_model_only_scenario_set_emits_no_historical_search_targets() -> None:
    model_only = {
        "baseline": "baseline",
        "scenarios": {
            "baseline": {"axis": "baseline"},
            "model-a": {"axis": "model", "changed_decision_ids": ["D_M1"]},
        },
    }
    result = diagnose_uncertainty(
        model_only,
        {"slice": {"baseline": [1, 1, 1], "model-a": [1, 2, 1]}},
        [gap("G_MODEL", ["D_M1"])],
    )
    assert result["slices"][0]["classification"] == "model_sensitivity"
    assert result["slices"][0]["changed_scenarios"]["evidence"] == []
    assert result["search_targets"] == []


def test_rejects_different_analysis_grid_between_slices() -> None:
    assignments = {
        "a": {name: [1, 1] for name in ("baseline", "evidence-a", "evidence-b", "model-a")},
        "b": {name: [1, 1, 1] for name in ("baseline", "evidence-a", "evidence-b", "model-a")},
    }

    with pytest.raises(ValueError, match="analysis grid"):
        diagnose_uncertainty(config(), assignments, [])
