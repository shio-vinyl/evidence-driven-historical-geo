from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases/crusader_states/public"
ROUNDS = CASE / "research/rounds"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _effects(document: dict, axis: str) -> dict[str, int]:
    rows = document["slices"][0]["scenario_effects"][axis]
    return {row["scenario"]: row["affected_grid_cells"] for row in rows}


def test_round_00_and_round_01_uncertainty_states_are_not_conflated() -> None:
    round_00 = _read(ROUNDS / "00-initial/uncertainty-diagnosis.json")
    by_slice = {row["slice"]: row for row in round_00["slices"]}
    assert {
        row["scenario"]: row["affected_grid_cells"]
        for row in by_slice[1130]["scenario_effects"]["evidence"]
    } == {
        "isolated-D_1130_ASCALON_SEED": 1,
        "isolated-D_1130_EDESSA_SEED": 257,
        "isolated-D_1130_TORTOSA_SEED": 0,
        "isolated-D_1130_TRIPOLI_SEED": 220,
    }
    assert {
        row["scenario"]: row["affected_grid_cells"]
        for row in by_slice[1187]["scenario_effects"]["evidence"]
    } == {
        "isolated-D_1187_CAIRO_SEED": 1162,
        "isolated-D_1187_JAFFA_SEED": 0,
    }

    round_01_1130 = _read(ROUNDS / "01-evidence-update/uncertainty-diagnosis-1130.json")
    round_01_1187 = _read(ROUNDS / "01-evidence-update/uncertainty-diagnosis-1187.json")
    assert _effects(round_01_1130, "evidence") == {
        "isolated-D_1130_ASCALON_SEED": 1,
        "isolated-D_1130_TORTOSA_SEED": 0,
    }
    assert _effects(round_01_1187, "evidence") == {}
    assert round_01_1187["slices"][0]["affected_grid_cells"]["evidence"] == 0


def test_round_01_baseline_delta_attributes_surface_change_without_accuracy_claim() -> None:
    delta = _read(ROUNDS / "01-evidence-update/round-delta.json")
    by_slice = {row["slice"]: row for row in delta["slices"]}
    assert by_slice[1130]["changed_grid_cells"] == 0
    assert by_slice[1187]["changed_grid_cells"] == 1162
    assert by_slice[1187]["changed_cell_transitions"] == [
        {"from": "unassigned", "to": "Ayyubid Sultanate", "grid_cells": 1162}
    ]
    assert "do not measure historical accuracy" in delta["interpretation_limit"]


def test_checked_in_evaluation_figures_declare_frozen_round_00_provenance() -> None:
    for name in ("reference-comparison.json", "uncertainty-zones.json"):
        report = _read(CASE / "figures" / name)
        assert report["evaluation_state"] == "round-00-initial"
        assert report["execution_path"] == "frozen-v0.1-compatibility"
        assert report["current_research_state_path"] == "research/rounds/01-evidence-update"

    english = (ROOT / "docs/research/comparative-evaluation.md").read_text(encoding="utf-8")
    chinese = (ROOT / "docs/research/comparative-evaluation.zh-CN.md").read_text(encoding="utf-8")
    assert "No updated held-out comparison count is claimed for Round 01" in english
    assert "项目没有声称得到 Round-01 的新版 held-out 比较计数" in chinese
