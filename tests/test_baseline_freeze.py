from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from historical_geo.pipeline import reconstruct


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "cases/crusader_states/public"
MANIFEST = PUBLIC / "baseline-manifest.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_baseline_manifest_matches_public_inputs_and_figures(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["manifest_version"] == "historical_geo.baseline.v0.1"
    assert manifest["case_id"] == "crusader-states-public-case"
    assert manifest["baseline_scenario"] == "reviewed-baseline"

    for relative, expected_hash in manifest["input_sha256"].items():
        assert _sha256(PUBLIC / relative) == expected_hash

    uncertainty = json.loads((PUBLIC / manifest["uncertainty_metrics_path"]).read_text())
    metric_names = (
        "stable_core",
        "model_sensitive_zone",
        "evidence_sensitive_zone",
        "unresolved_zone",
    )
    for slice_value, expected in manifest["uncertainty_percent_of_assessed"].items():
        actual = uncertainty["slices"][slice_value]
        assert {name: actual[name]["percent_of_assessed"] for name in metric_names} == expected
        assert 99.9 <= sum(expected.values()) <= 100.1

    # Reconstruct from an input-only copy: this deliberately excludes build/ and figures/.
    case_copy = tmp_path / "public-case"
    case_copy.mkdir()
    for relative in manifest["input_sha256"]:
        shutil.copy2(PUBLIC / relative, case_copy / relative)
    for slice_value, expected in manifest["slices"].items():
        run_dir = reconstruct(case_copy, int(slice_value), scenario=manifest["baseline_scenario"])
        surface = json.loads((run_dir / "boundary-hypotheses.geojson").read_text())
        entities = sorted(feature["properties"]["entity"] for feature in surface["features"])
        assert entities == expected["entities"]
