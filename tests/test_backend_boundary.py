from __future__ import annotations

from copy import deepcopy

import pytest

from historical_geo.backends import BACKENDS, get_backend
from historical_geo.backends.xtent_backend import compile_xtent_solver_input


def request() -> dict:
    return {
        "contract_version": "historical_geo.reconstruction_request.v0.2",
        "case_id": "backend-test", "slice": 1130, "scenario": "baseline",
        "grid": {"resolution": 1},
        "inputs": [
            {
                "decision_id": "POINT", "role": "control_point", "review_status": "admitted",
                "claim_ids": ["CLM_POINT"], "source_ids": ["SRC"], "rationale": "Point.",
                "parameters": {"entity": "Polity", "name": "City", "coordinates": [35, 31], "weight_class": "major"},
            },
            {
                "decision_id": "EXTENT", "role": "spatial_constraint", "review_status": "assumption",
                "claim_ids": [], "source_ids": [], "rationale": "Prior.", "assumption_reason": "Declared.",
                "parameters": {"constraint_kind": "extent_prior", "entity": "Polity", "reach_class": "normal"},
            },
            {
                "decision_id": "FRICTION", "role": "traversal_constraint", "review_status": "admitted",
                "claim_ids": ["CLM_FRICTION"], "source_ids": ["SRC"], "rationale": "Feature.",
                "parameters": {"constraint_kind": "friction_feature", "feature_id": "ridge", "strength": "soft"},
            },
        ],
    }


def test_xtent_backend_is_a_pure_legacy_structure_conversion() -> None:
    converted = compile_xtent_solver_input(request())
    assert converted["contract_version"] == "historical_geo.solver_input.v0.1"
    assert [item["decision_id"] for item in converted["seeds"]] == ["POINT"]
    assert [item["decision_id"] for item in converted["phases"]] == ["EXTENT"]
    assert [item["decision_id"] for item in converted["barriers"]] == ["FRICTION"]
    assert converted["seeds"][0]["parameters"]["weight_ordinal"] == "major"
    assert converted["phases"][0]["parameters"]["projection"] == "normal"
    assert "constraint_kind" not in converted["barriers"][0]["parameters"]
    assert converted["lineage"] == {
        "EXTENT": [], "FRICTION": ["CLM_FRICTION", "SRC"], "POINT": ["CLM_POINT", "SRC"],
    }
    assert BACKENDS == {"xtent": compile_xtent_solver_input}
    assert get_backend("xtent") is compile_xtent_solver_input


def test_xtent_backend_rejects_unknown_constraint_kind_and_missing_parameters() -> None:
    bad_kind = request()
    bad_kind["inputs"][2]["parameters"]["constraint_kind"] = "corridor_feature"
    with pytest.raises(ValueError, match="unsupported traversal constraint kind"):
        compile_xtent_solver_input(bad_kind)

    missing = request()
    del missing["inputs"][0]["parameters"]["coordinates"]
    with pytest.raises(ValueError, match="missing required parameters: coordinates"):
        compile_xtent_solver_input(missing)
