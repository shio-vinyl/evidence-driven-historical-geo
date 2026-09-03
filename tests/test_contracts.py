from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from historical_geo.contracts import validate_lineage_bundle, validate_schema

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIXTURE = ROOT / "cases/crusader_states/fixtures/synthetic_smoke/lineage.json"


def bundle() -> dict:
    return json.loads(FIXTURE.read_text())


def codes(result) -> set[str]:
    return {x.code for x in result.errors}


def test_flagship_fixture_matches_json_schema_and_semantic_contract() -> None:
    data = bundle()
    assert not validate_schema(data, SCHEMAS / "lineage-bundle.schema.json")
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert result.ok
    assert not result.research_gaps


def test_assumption_can_be_numeric_free_and_source_free_when_labeled() -> None:
    data = bundle()
    phase = next(x for x in data["model_decisions"] if x["decision_id"] == "D_WEST_PHASE")
    assert phase["evidence_ids"] == []
    assert phase["source_ids"] == []
    assert phase["assumption_reason"]
    assert validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json").ok


def test_accepted_decision_without_evidence_fails_and_emits_gap() -> None:
    data = bundle()
    decision = next(x for x in data["model_decisions"] if x["decision_id"] == "D_WEST_SEED")
    decision["evidence_ids"] = []
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert "missing_evidence" in codes(result)
    assert result.research_gaps[0]["decision_id"] == "D_WEST_SEED"


def test_event_or_route_cannot_be_an_allocation_seed() -> None:
    data = bundle()
    decision = next(x for x in data["model_decisions"] if x["decision_id"] == "D_ROUTE_EXCLUDED")
    decision["status"] = "accepted"
    decision["is_allocation_input"] = True
    decision["parameters"].update({"coordinates": [5.0, 3.0], "coordinates_status": "verified"})
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert "non_point_seed" in codes(result)


def test_unknown_coordinates_cannot_become_seed() -> None:
    data = bundle()
    decision = next(x for x in data["model_decisions"] if x["decision_id"] == "D_WEST_SEED")
    decision["parameters"]["coordinates_status"] = "unknown"
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert "unknown_coordinates" in codes(result)


def test_display_only_record_cannot_enter_allocation() -> None:
    data = bundle()
    decision = next(x for x in data["model_decisions"] if x["decision_id"] == "D_EVENT_DISPLAY_ONLY")
    decision["status"] = "accepted"
    decision["is_allocation_input"] = True
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert "schema_error" in codes(result)


def test_raw_model_float_is_rejected() -> None:
    data = bundle()
    decision = next(x for x in data["model_decisions"] if x["decision_id"] == "D_WEST_PHASE")
    decision["parameters"]["decay"] = 0.08
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert "raw_number_forbidden" in codes(result)


def test_natural_barrier_requires_evidence_or_assumption() -> None:
    data = bundle()
    decision = next(x for x in data["model_decisions"] if x["decision_id"] == "D_SYNTHETIC_BARRIER")
    decision["status"] = "accepted"
    decision["evidence_ids"] = ["E_WEST_POINT"]
    decision["source_ids"] = ["SRC_FIXTURE"]
    decision.pop("assumption_reason")
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert "unsupported_natural_role" in codes(result)


def test_all_public_json_schemas_are_valid_draft_2020_12() -> None:
    from jsonschema import Draft202012Validator

    for path in sorted(SCHEMAS.glob("*.schema.json")):
        Draft202012Validator.check_schema(json.loads(path.read_text()))


def test_decision_must_carry_sources_linked_through_evidence() -> None:
    data = bundle()
    decision = next(x for x in data["model_decisions"] if x["decision_id"] == "D_WEST_SEED")
    decision["source_ids"] = []
    result = validate_lineage_bundle(data, SCHEMAS / "lineage-bundle.schema.json")
    assert "incomplete_source_lineage" in codes(result)
