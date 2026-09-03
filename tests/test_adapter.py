from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from historical_geo.adapter import build_solver_input, load_case, write_solver_input

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cases/crusader_states/fixtures/synthetic_smoke"


def test_adapter_outputs_only_reviewed_allocation_decisions() -> None:
    result = build_solver_input(SOURCE, 1130)
    assert len(result["seeds"]) == 2
    assert len(result["phases"]) == 2
    assert len(result["barriers"]) == 1
    assert result["gates"] == []
    assert result["corridors"] == []
    ids = set(result["lineage"])
    assert "D_EVENT_DISPLAY_ONLY" not in ids
    assert "D_ROUTE_EXCLUDED" not in ids
    assert {x["decision_id"] for x in result["seeds"]} == {"D_WEST_SEED", "D_EAST_SEED"}
    assert all("assumption_reason" in x for x in result["phases"] + result["barriers"])


def test_adapter_serialization_is_deterministic(tmp_path: Path) -> None:
    case = tmp_path / "case"
    shutil.copytree(SOURCE, case)
    first = write_solver_input(case, 1130).read_bytes()
    second = write_solver_input(case, 1130).read_bytes()
    assert first == second


def test_case_rejects_absolute_input_path(tmp_path: Path) -> None:
    case = tmp_path / "case"
    shutil.copytree(SOURCE, case)
    data = json.loads((case / "case.json").read_text())
    data["grid"]["land_path"] = "/tmp/private-land.geojson"
    (case / "case.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="must be relative"):
        load_case(case)


def test_case_rejects_parent_traversal(tmp_path: Path) -> None:
    case = tmp_path / "case"
    shutil.copytree(SOURCE, case)
    data = json.loads((case / "case.json").read_text())
    data["lineage_path"] = "../lineage.json"
    (case / "case.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="escapes"):
        load_case(case)
