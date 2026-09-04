from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from historical_geo.adapter import load_case
from historical_geo.cli import validate_case
from historical_geo.prospective import (
    astronomical_year_from_bce,
    effective_prospective_state,
    validate_preregistration,
)
from historical_geo.research_case import compile_case_request


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases/sennacherib_701_southern_levant/public"


def _load(name: str) -> dict:
    return json.loads((CASE / name).read_text(encoding="utf-8"))


def test_checked_in_sennacherib_case_is_valid_sealed_and_terminal_without_reconstruction() -> None:
    result = validate_case(CASE)
    assert result["ok"], result["errors"]
    case = load_case(CASE)
    assert case["research_stage"] == "evidence_collection"
    assert case["reconstruction_ready"] is False
    lifecycle = _load("lifecycle.json")
    assert lifecycle["baseline"]["freeze_commit"] == "bf513e88c18fba2dd8636b4d89b06950a497706d"
    assert [item["round_id"] for item in lifecycle["rounds"]] == ["01-non-map-evidence"]
    assert lifecycle["effective_state"]["stage"] == "completed_no_reconstruction"
    assert lifecycle["effective_state"]["terminal_outcome"] == "completed_no_reconstruction"
    assert lifecycle["effective_state"]["held_out_isolation"] == "metadata_only_unviewed"
    effective = effective_prospective_state(CASE, case)
    assert effective["stage"] == "completed_no_reconstruction"
    assert effective["reconstruction_ready"] is False
    assert effective["terminal_outcome"] == "completed_no_reconstruction"
    with pytest.raises(ValueError, match="not reconstruction-ready"):
        compile_case_request(CASE, "701-bce-campaign-horizon")


def test_post_freeze_budget_gap_closure_and_gate_are_exact() -> None:
    round_dir = CASE / "research/rounds/01-non-map-evidence"
    budget = json.loads((round_dir / "budget.json").read_text(encoding="utf-8"))
    assert budget["consumed"]["queries"] == 16
    assert budget["consumed"]["content_record_checks"] == 20
    assert budget["consumed"]["sources_admitted"] == 7
    assert set(budget["consumed"]["per_gap_follow_ups"].values()) == {2}
    gate = json.loads((round_dir / "gate.json").read_text(encoding="utf-8"))
    assert gate["overall_passed"] is False
    assert gate["decision"] == "completed_no_reconstruction"
    assert gate["polygon_generated"] is False
    assert gate["modeling_status"]["modeled_entity_roster"] == []
    assert gate["modeling_status"]["scenarios_run"] == []
    gaps = json.loads((round_dir / "gaps.json").read_text(encoding="utf-8"))
    assert {item["status"] for item in gaps["gap_updates"]} == {
        "closed_supported",
        "closed_unresolved",
        "closed_excluded",
    }


def test_post_freeze_round_hashes_match_bytes() -> None:
    round_dir = CASE / "research/rounds/01-non-map-evidence"
    manifest = json.loads((round_dir / "round-manifest.json").read_text(encoding="utf-8"))
    for artifact in manifest["files"]:
        assert hashlib.sha256((round_dir / artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]


def test_post_freeze_sources_preserve_lineages_and_map_seal() -> None:
    source_doc = json.loads(
        (CASE / "research/rounds/01-non-map-evidence/sources.json").read_text(encoding="utf-8")
    )
    records = source_doc["records"]
    assert sum(record["disposition"] == "admitted" for record in records) == 7
    assert all(record["map_body_accessed"] is False for record in records)
    assert all(check["map_body_accessed"] is False for check in source_doc["content_checks"])
    lineage = {record["source_id"]: record["lineage_id"] for record in records}
    assert lineage["SRC_R1_MET_2014"] == "ASSYRIAN_ROYAL_THIRD_CAMPAIGN_TRADITION"
    held_out = _load("held-out-map-register.json")
    assert held_out["isolation_state"] == "metadata_only_unviewed"
    for candidate in held_out["candidates"]:
        assert candidate["content_access_status"] == "not_viewed"
        assert candidate["body_viewed"] is False
        assert candidate["thumbnail_viewed"] is False


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
