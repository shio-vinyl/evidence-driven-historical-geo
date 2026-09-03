from __future__ import annotations

import json
from pathlib import Path
import shutil

from historical_geo.cli import validate_case
from historical_geo.pipeline import audit_surface, reconstruct

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "cases/crusader_states/public"


def copied_public_case(tmp_path: Path) -> Path:
    target = tmp_path / "public-case"
    shutil.copytree(PUBLIC_CASE, target, ignore=shutil.ignore_patterns("build", "figures"))
    return target


def test_public_lineage_and_fixture_manifest_are_self_contained() -> None:
    assert validate_case(PUBLIC_CASE)["ok"]
    manifest = json.loads((PUBLIC_CASE / "fixture-manifest.json").read_text())
    assert {item["source_id"] for item in manifest["source_inputs"]} == {
        "SRC_GEONAMES",
        "SRC_NATURAL_EARTH",
    }
    assert all(not Path(item["path"]).is_absolute() for item in manifest["files"])


def test_public_case_retains_expected_entities_in_both_slices(tmp_path: Path) -> None:
    case = copied_public_case(tmp_path)
    expected = {
        1130: {
            "Burid Damascus",
            "County of Edessa",
            "County of Tripoli",
            "Kingdom of Jerusalem",
            "Principality of Antioch",
        },
        1187: {
            "Ayyubid Sultanate",
            "County of Tripoli",
            "Kingdom of Jerusalem",
            "Principality of Antioch",
        },
    }
    for slice_value, entities in expected.items():
        run_dir = reconstruct(case, slice_value)
        assert all(audit_surface(run_dir / "boundary-hypotheses.geojson", sorted(entities)).values())
        surface = json.loads((run_dir / "boundary-hypotheses.geojson").read_text())
        assert {feature["properties"]["entity"] for feature in surface["features"]} == entities


def test_reviewed_figure_qa_and_captions_exist() -> None:
    qa = json.loads((PUBLIC_CASE / "figures/figure-qa.json").read_text())
    assert qa["all_nonblank"]
    assert len(qa["figures"]) == 6
    captions = (PUBLIC_CASE / "figures/README.md").read_text()
    assert "boundary hypotheses" in captions
    assert "not evidence" in captions


def test_reviewed_baseline_excludes_disputed_seeds_and_inclusive_keeps_them() -> None:
    from historical_geo.adapter import build_solver_input

    baseline_1130 = build_solver_input(PUBLIC_CASE, 1130, scenario="reviewed-baseline")
    inclusive_1130 = build_solver_input(PUBLIC_CASE, 1130, scenario="inclusive")
    baseline_1187 = build_solver_input(PUBLIC_CASE, 1187, scenario="reviewed-baseline")
    inclusive_1187 = build_solver_input(PUBLIC_CASE, 1187, scenario="inclusive")
    assert {x["parameters"]["name"] for x in baseline_1130["seeds"]}.isdisjoint({"Ascalon", "Tortosa"})
    assert {"Ascalon", "Tortosa"} <= {x["parameters"]["name"] for x in inclusive_1130["seeds"]}
    assert {x["parameters"]["name"] for x in baseline_1187["seeds"]}.isdisjoint({"Cairo", "Jaffa"})
    assert {"Cairo", "Jaffa"} <= {x["parameters"]["name"] for x in inclusive_1187["seeds"]}


def test_claim_decision_table_covers_all_seven_load_bearing_gaps() -> None:
    decisions = json.loads((PUBLIC_CASE / "historical-claim-decisions.json").read_text())
    assert len(decisions["groups"]) == 7
    assert {x["decision"] for x in decisions["groups"]} <= {"KEEP", "DOWNGRADE", "REMOVE", "DISPUTED"}


def test_reference_and_uncertainty_reports_avoid_accuracy_claims() -> None:
    comparison = json.loads((PUBLIC_CASE / "figures/reference-comparison.json").read_text())
    uncertainty = json.loads((PUBLIC_CASE / "figures/uncertainty-zones.json").read_text())
    assert comparison["boundary_metrics_computed"] is False
    assert comparison["parameter_tuning_from_references"] is False
    assert "not a probability" in uncertainty["interpretation"]
    for metrics in uncertainty["slices"].values():
        total = sum(metrics[name]["percent_of_assessed"] for name in (
            "stable_core", "model_sensitive_zone", "evidence_sensitive_zone", "unresolved_zone"
        ))
        assert 99.9 <= total <= 100.1
