from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest
from jsonschema import Draft202012Validator

from historical_geo.adapter import load_case
from historical_geo.cli import validate_case
from historical_geo.prospective import validate_prospective_case
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


def test_checked_in_prospective_case_is_valid_and_not_reconstruction_ready() -> None:
    result = validate_case(CASE)
    assert result["ok"], result["errors"]
    case = load_case(CASE)
    assert case["research_stage"] == "evidence_collection"
    assert case["reconstruction_ready"] is False
    with pytest.raises(ValueError, match="not reconstruction-ready"):
        compile_case_request(CASE, "780-796")


def test_preregistration_and_held_out_schemas_are_valid_draft_2020_12() -> None:
    for name in ("preregistration.schema.json", "held-out-map-register.schema.json"):
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


def test_case_contains_no_map_body_or_polygon_artifact() -> None:
    forbidden_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".svg"}
    files = [path for path in CASE.rglob("*") if path.is_file()]
    assert not [path for path in files if path.suffix.lower() in forbidden_suffixes]
    assert not [path for path in files if path.name.startswith("boundary-hypotheses")]
