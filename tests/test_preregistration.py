from __future__ import annotations

import json
import hashlib
from pathlib import Path
import shutil

import pytest
from jsonschema import Draft202012Validator

from historical_geo.adapter import load_case
from historical_geo.cli import validate_case
from historical_geo.prospective import effective_prospective_state, validate_prospective_case
from historical_geo.research_case import compile_case_request


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases/mercia_welsh_frontier/public"


def _copy(tmp_path: Path) -> Path:
    target = tmp_path / "prospective"
    shutil.copytree(CASE, target)
    return target


def _codes(path: Path) -> set[str]:
    case = load_case(path)
    return {issue.code for issue in validate_prospective_case(path, case).errors}


def _write_json(path: Path, document: dict) -> None:
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _rehash_round(case: Path, round_id: str = "01-non-map-evidence") -> None:
    round_dir = case / "research" / "rounds" / round_id
    manifest_path = round_dir / "round-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest["files"]:
        entry["sha256"] = hashlib.sha256((round_dir / entry["path"]).read_bytes()).hexdigest()
    _write_json(manifest_path, manifest)
    lifecycle_path = case / "lifecycle.json"
    lifecycle = json.loads(lifecycle_path.read_text())
    lifecycle["rounds"][0]["manifest_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    _write_json(lifecycle_path, lifecycle)


def test_checked_in_prospective_case_is_valid_and_terminal_without_reconstruction() -> None:
    result = validate_case(CASE)
    assert result["ok"], result["errors"]
    case = load_case(CASE)
    assert case["research_stage"] == "evidence_collection"
    assert case["reconstruction_ready"] is False
    effective = effective_prospective_state(CASE, case)
    assert effective["stage"] == "completed_no_reconstruction"
    assert effective["terminal_outcome"] == "completed_no_reconstruction"
    assert effective["reconstruction_ready"] is False
    assert len(effective["sources"]) == 17
    assert len(effective["observations"]) == 24
    assert len(effective["claims"]) == 14
    assert len(effective["model_decisions"]) == 10
    assert set(effective["gap_statuses"].values()) <= {"closed_unresolved", "closed_excluded"}
    with pytest.raises(ValueError, match="not reconstruction-ready"):
        compile_case_request(CASE, "780-796")


def test_preregistration_and_held_out_schemas_are_valid_draft_2020_12() -> None:
    for name in ("preregistration.schema.json", "held-out-map-register.schema.json", "prospective-lifecycle.schema.json"):
        Draft202012Validator.check_schema(json.loads((ROOT / "schemas" / name).read_text()))


def test_held_out_access_flag_breaks_the_seal(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    path = case / "held-out-map-register.json"
    data = json.loads(path.read_text())
    data["candidates"][0]["body_viewed"] = True
    data["candidates"][0]["content_access_status"] = "viewed"
    path.write_text(json.dumps(data))
    codes = _codes(case)
    assert "schema_error" in codes or "held_out_content_accessed" in codes


def test_held_out_id_cannot_leak_into_research_artifacts(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    path = case / "research-scenarios.json"
    data = json.loads(path.read_text())
    data["contaminating_note"] = "MAP_HILL_1981_ATLAS"
    path.write_text(json.dumps(data))
    assert "held_out_reference_leak" in _codes(case)


def test_historical_map_source_cannot_enter_prospective_bundle(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    access_path = case / "source-access-rights.json"
    access = json.loads(access_path.read_text())
    access["records"][0]["evidence_class"] = "historical_territorial_map"
    access_path.write_text(json.dumps(access))
    assert "territorial_map_in_research_bundle" in _codes(case)


def test_sealed_case_rejects_map_body_and_boundary_outputs(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    (case / "candidate.png").write_bytes(b"not really an image")
    (case / "boundary-hypotheses.geojson").write_text("{}")
    codes = _codes(case)
    assert "map_body_file_in_sealed_case" in codes
    assert "premature_reconstruction_artifact" in codes


def test_freeze_manifest_detects_changed_preregistered_artifact(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    path = case / "spatial-input-contract.json"
    data = json.loads(path.read_text())
    data["inputs_present"] = True
    path.write_text(json.dumps(data))
    assert "freeze_hash_mismatch" in _codes(case)


def test_round_manifest_detects_historical_round_tampering(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    path = case / "research/rounds/01-non-map-evidence/claims.json"
    data = json.loads(path.read_text())
    data["claims"][0]["statement"] = "tampered"
    _write_json(path, data)
    assert "round_file_hash_mismatch" in _codes(case)


def test_validator_rejects_stage_jump_even_after_rehash(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    path = case / "research/rounds/01-non-map-evidence/round.json"
    data = json.loads(path.read_text())
    data["transition"]["from"] = "preregistered"
    _write_json(path, data)
    _rehash_round(case)
    assert "invalid_lifecycle_transition" in _codes(case)


def test_validator_rejects_budget_overrun_even_after_rehash(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    round_dir = case / "research/rounds/01-non-map-evidence"
    query_path = round_dir / "queries.json"
    queries = json.loads(query_path.read_text())
    template = dict(queries["queries"][-1])
    for number in (24, 25):
        queries["queries"].append({**template, "query_id": f"Q{number:03d}", "query": f"over-budget query {number}"})
    _write_json(query_path, queries)
    budget_path = round_dir / "budget.json"
    budget = json.loads(budget_path.read_text())
    budget["consumed"]["queries"] = 25
    _write_json(budget_path, budget)
    lifecycle_path = case / "lifecycle.json"
    lifecycle = json.loads(lifecycle_path.read_text())
    lifecycle["effective_state"]["budget_consumed"]["queries"] = 25
    _write_json(lifecycle_path, lifecycle)
    _rehash_round(case)
    assert "research_budget_exceeded" in _codes(case)


def test_held_out_identifier_cannot_leak_into_reviewed_round(tmp_path: Path) -> None:
    case = _copy(tmp_path)
    held_out = json.loads((case / "held-out-map-register.json").read_text())
    token = held_out["candidate_order"][0]
    path = case / "research/rounds/01-non-map-evidence/queries.json"
    data = json.loads(path.read_text())
    data["queries"][0]["result_summary"] = token
    _write_json(path, data)
    _rehash_round(case)
    assert "held_out_reference_leak" in _codes(case)


def test_case_contains_no_map_body_or_polygon_artifact() -> None:
    forbidden_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".svg"}
    files = [path for path in CASE.rglob("*") if path.is_file()]
    assert not [path for path in files if path.suffix.lower() in forbidden_suffixes]
    assert not [path for path in files if path.name.startswith("boundary-hypotheses")]
