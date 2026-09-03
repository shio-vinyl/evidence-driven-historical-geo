from __future__ import annotations

import json
from pathlib import Path
import shutil

from historical_geo.adapter import build_solver_input
from historical_geo.backends.xtent_backend import compile_xtent_solver_input
from historical_geo.research_case import compile_case_request, run_research_loop
from historical_geo.research_contracts import (
    validate_search_targets,
    validate_uncertainty_diagnosis,
)

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "cases/crusader_states/public"


def _copied_case(tmp_path: Path) -> Path:
    target = tmp_path / "case"
    shutil.copytree(PUBLIC_CASE, target, ignore=shutil.ignore_patterns("build", "figures"))
    return target


def test_v02_compiler_preserves_legacy_xtent_inputs() -> None:
    for slice_value in (1130, 1187):
        for scenario in (
            "reviewed-baseline",
            "verified-only",
            "inclusive",
            "flat-natural",
            "projection-normal",
            "projection-expansive",
        ):
            legacy = build_solver_input(PUBLIC_CASE, slice_value, scenario=scenario)
            compiled = compile_xtent_solver_input(
                compile_case_request(PUBLIC_CASE, slice_value, scenario)
            )
            assert compiled == legacy


def test_research_loop_writes_valid_ranked_targets(tmp_path: Path) -> None:
    case = _copied_case(tmp_path)
    diagnosis_path, targets_path = run_research_loop(case, 1130)
    bundle = json.loads((case / "research-bundle.json").read_text())
    diagnosis = json.loads(diagnosis_path.read_text())
    targets = json.loads(targets_path.read_text())
    assert validate_uncertainty_diagnosis(diagnosis, bundle).ok
    assert validate_search_targets(targets, bundle).ok
    priorities = [target["priority_basis"]["affected_grid_cells"] for target in targets["targets"]]
    assert priorities == sorted(priorities, reverse=True)
    assert priorities
