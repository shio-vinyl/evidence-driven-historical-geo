from __future__ import annotations

import json
from pathlib import Path
import shutil

from historical_geo.backends.xtent_backend import compile_xtent_solver_input
from historical_geo.cli import main
from historical_geo.contracts import validate_schema
from historical_geo.research_case import _diagnostic_config, compile_case_request, run_research_loop
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


def test_v02_compiler_produces_deterministic_xtent_compatible_inputs() -> None:
    for slice_value in (1130, 1187):
        for scenario in (
            "reviewed-baseline",
            "verified-only",
            "inclusive",
            "flat-natural",
            "projection-normal",
            "projection-expansive",
        ):
            compiled = compile_xtent_solver_input(
                compile_case_request(PUBLIC_CASE, slice_value, scenario)
            )
            assert not validate_schema(compiled, ROOT / "schemas/solver-input.schema.json")
            assert compiled == compile_xtent_solver_input(
                compile_case_request(PUBLIC_CASE, slice_value, scenario)
            )
            assert {record["parameters"]["entity"] for record in compiled["phases"]} == {
                record["parameters"]["entity"] for record in compiled["seeds"]
            }


def test_default_cli_path_validates_and_runs_through_v02_compiler(tmp_path: Path) -> None:
    case = _copied_case(tmp_path)
    assert main(["validate", str(case)]) == 0
    assert main(["run", str(case), "--slice", "1130"]) == 0
    effective = json.loads((case / "build/run-1130/effective-solver-input.json").read_text())
    expected = compile_xtent_solver_input(compile_case_request(case, 1130))
    assert effective == expected


def test_default_cli_rejects_v01_only_fixture_with_explicit_legacy_route(tmp_path: Path) -> None:
    fixture = ROOT / "cases/crusader_states/fixtures/synthetic_smoke"
    case = tmp_path / "fixture"
    shutil.copytree(fixture, case)
    assert main(["validate", str(case)]) == 1
    assert main(["legacy-validate", str(case)]) == 0


def test_default_validation_checks_reviewed_round_artifacts(tmp_path: Path) -> None:
    case = _copied_case(tmp_path)
    diagnosis_path = case / "research/rounds/01-evidence-update/uncertainty-diagnosis-1187.json"
    diagnosis = json.loads(diagnosis_path.read_text())
    diagnosis["slices"][0]["changed_decision_ids"]["all"].append("D_MISSING")
    diagnosis_path.write_text(json.dumps(diagnosis))

    assert main(["validate", str(case)]) == 1


def test_default_validation_checks_explicit_scenario_allowlists(tmp_path: Path) -> None:
    case = _copied_case(tmp_path)
    scenarios_path = case / "research-scenarios.json"
    scenarios = json.loads(scenarios_path.read_text())
    del scenarios["scenarios"]["reviewed-baseline"]["included_decision_ids"]
    scenarios_path.write_text(json.dumps(scenarios))

    assert main(["validate", str(case)]) == 1


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


def test_diagnostic_config_derives_one_counterfactual_per_evidence_decision() -> None:
    expected = {
        1130: {
            "D_1130_ASCALON_SEED",
            "D_1130_TORTOSA_SEED",
        },
        1187: set(),
    }
    for slice_value, decision_ids in expected.items():
        config = _diagnostic_config(PUBLIC_CASE, slice_value)
        isolated = [
            profile
            for name, profile in config["scenarios"].items()
            if name.startswith("isolated-")
        ]
        assert {profile["changed_decision_ids"][0] for profile in isolated} == decision_ids
        assert all(len(profile["changed_decision_ids"]) == 1 for profile in isolated)


def test_diagnostic_config_allows_a_model_only_slice(tmp_path: Path) -> None:
    case = _copied_case(tmp_path)
    scenarios_path = case / "research-scenarios.json"
    scenarios = json.loads(scenarios_path.read_text())
    scenarios["scenarios"] = {
        name: definition
        for name, definition in scenarios["scenarios"].items()
        if name in {"reviewed-baseline", "flat-natural"}
    }
    scenarios_path.write_text(json.dumps(scenarios))

    config = _diagnostic_config(case, 1187)
    assert set(config["scenarios"]) == {"reviewed-baseline", "flat-natural"}


def test_research_loop_runs_a_model_only_slice_without_inventing_search_targets(tmp_path: Path) -> None:
    case = _copied_case(tmp_path)
    diagnosis_path, targets_path = run_research_loop(case, 1187)
    diagnosis = json.loads(diagnosis_path.read_text())
    targets = json.loads(targets_path.read_text())

    assert diagnosis["slices"][0]["classification"] == "model_sensitivity"
    assert diagnosis["slices"][0]["changed_scenarios"]["evidence"] == []
    assert targets["targets"] == []


def test_research_loop_uses_isolated_counterfactual_effects_for_priority(tmp_path: Path) -> None:
    case = _copied_case(tmp_path)
    diagnosis_path, targets_path = run_research_loop(case, 1130)
    diagnosis = json.loads(diagnosis_path.read_text())
    targets = json.loads(targets_path.read_text())

    effects = {
        effect["changed_decision_ids"][0]: effect["affected_grid_cells"]
        for effect in diagnosis["slices"][0]["scenario_effects"]["evidence"]
    }
    assert effects == {
        "D_1130_ASCALON_SEED": 1,
        "D_1130_TORTOSA_SEED": 0,
    }
    priorities = {
        target["decision_ids"][0]: target["priority_basis"]["affected_grid_cells"]
        for target in targets["targets"]
    }
    assert priorities == {
        "D_1130_ASCALON_SEED": 1,
    }
