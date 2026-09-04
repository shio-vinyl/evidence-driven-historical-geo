from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from historical_geo.adapter import load_case
from historical_geo.cli import validate_case
from historical_geo.prospective import astronomical_year_from_bce, validate_preregistration
from historical_geo.research_case import compile_case_request


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases/sennacherib_701_southern_levant/public"


def _load(name: str) -> dict:
    return json.loads((CASE / name).read_text(encoding="utf-8"))


def test_checked_in_sennacherib_case_is_valid_sealed_and_not_reconstruction_ready() -> None:
    result = validate_case(CASE)
    assert result["ok"], result["errors"]
    case = load_case(CASE)
    assert case["research_stage"] == "evidence_collection"
    assert case["reconstruction_ready"] is False
    lifecycle = _load("lifecycle.json")
    assert lifecycle["baseline"]["freeze_commit"] == "bf513e88c18fba2dd8636b4d89b06950a497706d"
    assert lifecycle["rounds"] == []
    assert lifecycle["effective_state"]["held_out_isolation"] == "metadata_only_unviewed"
    with pytest.raises(ValueError, match="not reconstruction-ready"):
        compile_case_request(CASE, "701-bce-campaign-horizon")


def test_feasibility_budget_and_go_thresholds_are_frozen() -> None:
    audit = _load("feasibility-audit.json")
    assert audit["decision"] == "GO"
    assert audit["budget_consumed"] == {
        "content_catalog_checks": 10,
        "held_out_candidates_registered": 1,
        "held_out_metadata_queries": 3,
        "preliminary_sources_admitted": 6,
        "queries": 12,
    }
    assert len(audit["query_log"]) == 12
    assert len(audit["content_catalog_check_log"]) == 10
    assert len(audit["candidate_spatial_constraints"]) == 12
    assert all(item["passed"] for item in audit["go_thresholds"])


def test_bce_campaign_horizon_uses_explicit_era_and_exact_astronomical_conversion() -> None:
    prereg = _load("preregistration.json")
    temporal = prereg["temporal_scope"]
    assert temporal["calendar"] == "historical_bce_year_label"
    assert temporal["era"] == "BCE"
    assert temporal["year_bce"] == 701
    assert temporal["temporal_resolution"] == "campaign_horizon"
    assert temporal["astronomical_year_numbering"]["equivalent_year"] == -700
    assert astronomical_year_from_bce(701) == -700
    assert astronomical_year_from_bce(1) == 0
    with pytest.raises(ValueError, match="positive integer"):
        astronomical_year_from_bce(0)


def test_bce_contract_rejects_wrong_conversion_and_negative_iso_surrogate() -> None:
    prereg = _load("preregistration.json")
    prereg["temporal_scope"]["astronomical_year_numbering"]["equivalent_year"] = -701
    result = validate_preregistration(prereg)
    assert "astronomical_year_mismatch" in {issue.code for issue in result.errors}

    prereg = _load("preregistration.json")
    prereg["temporal_scope"]["chronology_uncertainty"] = "-0700-01-01"
    result = validate_preregistration(prereg)
    assert "negative_iso_bce_date" in {issue.code for issue in result.errors}


def test_assyrian_parallel_witnesses_share_one_declared_lineage() -> None:
    access = _load("source-access-rights.json")
    lineage_by_source = {record["source_id"]: record["lineage_id"] for record in access["records"]}
    assert lineage_by_source["SRC_ORACC_Q003496"] == lineage_by_source["SRC_ORACC_Q003945"]
    assert "not independent" in access["lineage_rule"]


def test_sennacherib_freeze_manifest_detects_mutation(tmp_path: Path) -> None:
    target = tmp_path / "case"
    shutil.copytree(CASE, target)
    path = target / "spatial-input-contract.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["inputs_present"] = True
    path.write_text(json.dumps(data), encoding="utf-8")
    result = validate_case(target)
    assert "freeze_hash_mismatch" in {issue["code"] for issue in result["errors"]}


def test_sennacherib_case_contains_no_map_body_polygon_or_negative_iso_date() -> None:
    forbidden_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".svg", ".geojson"}
    files = [path for path in CASE.rglob("*") if path.is_file()]
    assert not [path for path in files if path.suffix.lower() in forbidden_suffixes]
    assert not [path for path in files if path.name.startswith("boundary-hypotheses")]
    for name in ("preregistration.json", "spatial-input-contract.json"):
        text = (CASE / name).read_text(encoding="utf-8")
        assert '"target_interval_start"' not in text
        assert '"target_interval_end"' not in text


def test_sennacherib_freeze_hashes_match_bytes() -> None:
    freeze = _load("preregistration-freeze.json")
    for artifact in freeze["frozen_artifacts"]:
        assert hashlib.sha256((CASE / artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
