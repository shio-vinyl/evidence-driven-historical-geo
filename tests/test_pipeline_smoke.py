from __future__ import annotations

import json
from pathlib import Path
import shutil

from historical_geo.cli import main
from historical_geo.pipeline import _enforce_seed_ownership, _nearest_land_cell, audit_surface, reconstruct
from historical_geo.render import render_surface

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cases/crusader_states/fixtures/synthetic_smoke"


def copied_case(tmp_path: Path) -> Path:
    target = tmp_path / "case"
    shutil.copytree(SOURCE, target)
    return target


def test_reconstruct_materializes_every_entity_with_lineage(tmp_path: Path) -> None:
    case = copied_case(tmp_path)
    run_dir = reconstruct(case, 1130)
    surface = json.loads((run_dir / "boundary-hypotheses.geojson").read_text())
    assert [x["properties"]["entity"] for x in surface["features"]] == ["Fixture East", "Fixture West"]
    assert all(x["properties"]["model_label"] == "boundary_hypothesis" for x in surface["features"])
    assert all(x["properties"]["decision_ids"] for x in surface["features"])
    assert all(x["properties"]["uncertainty"] == "assumption-heavy" for x in surface["features"])
    assert all(audit_surface(run_dir / "boundary-hypotheses.geojson", ["Fixture East", "Fixture West"]).values())
    manifest = json.loads((run_dir / "run-manifest.json").read_text())
    assert manifest["entity_counts"] == {"expected": 2, "materialized": 2}
    assert all(manifest["validation"].values())


def test_minimum_renderer_is_nonblank_and_semantic(tmp_path: Path) -> None:
    case = copied_case(tmp_path)
    run_dir = reconstruct(case, 1130)
    image = render_surface(run_dir, title="Synthetic boundary hypotheses")
    qa = json.loads((run_dir / "render-qa.json").read_text())
    assert image.exists() and image.stat().st_size > 1000
    assert qa["nonblank"]
    assert qa["model_labels"] == ["boundary_hypothesis"]
    assert qa["feature_count"] == 2


def test_one_command_path_runs_validate_to_render(tmp_path: Path) -> None:
    case = copied_case(tmp_path)
    assert main(["run", str(case), "--slice", "1130"]) == 0
    run_dir = case / "build/run-1130"
    assert (run_dir / "effective-solver-input.json").exists()
    assert (run_dir / "boundary-hypotheses.geojson").exists()
    assert (run_dir / "run-manifest.json").exists()
    assert (run_dir / "boundary-hypotheses.png").exists()
    assert main(["audit", str(case), "--slice", "1130"]) == 0


def test_projected_case_transforms_fixture_geometries_and_seeds(tmp_path: Path) -> None:
    case_dir = tmp_path / "projected"
    shutil.copytree(SOURCE, case_dir)
    case = json.loads((case_dir / "case.json").read_text())
    case["grid"]["crs"] = "+proj=lcc +lat_1=1 +lat_2=5 +lat_0=3 +lon_0=5 +datum=WGS84 +units=m +no_defs"
    case["grid"]["resolution"] = 25_000
    (case_dir / "case.json").write_text(json.dumps(case))

    run_dir = reconstruct(case_dir, 1130)
    surface = json.loads((run_dir / "boundary-hypotheses.geojson").read_text())
    assert {feature["properties"]["entity"] for feature in surface["features"]} == {
        "Fixture East",
        "Fixture West",
    }
    assert audit_surface(run_dir / "boundary-hypotheses.geojson", ["Fixture East", "Fixture West"]) == {
        "valid": True,
        "non_overlapping": True,
        "entities_retained": True,
    }


def test_flat_scenario_removes_barrier_from_effective_input(tmp_path: Path) -> None:
    case = copied_case(tmp_path)
    run_dir = reconstruct(case, 1130, scenario="flat")
    assert run_dir.name == "run-1130-flat-natural"
    effective = json.loads((run_dir / "effective-solver-input.json").read_text())
    assert effective["barriers"] == []
    manifest = json.loads((run_dir / "run-manifest.json").read_text())
    assert "-flat-natural-" in manifest["run_id"]


def test_nearest_land_cell_is_deterministic() -> None:
    import numpy as np
    mask = np.zeros((5, 5), dtype=bool)
    mask[1, 2] = True
    mask[2, 1] = True
    assert _nearest_land_cell(mask, 2, 2) == (1, 2)


def test_reviewed_seed_cell_ownership_is_enforced() -> None:
    import numpy as np
    label = np.ones((3, 3), dtype=int)
    result = _enforce_seed_ownership(label, ["Strong", "Small"], {"Strong": [(0, 0, 4.0)], "Small": [(1, 1, 1.2)]})
    assert result[1, 1] == 2
