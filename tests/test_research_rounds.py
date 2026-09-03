from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from historical_geo.adapter import build_solver_input
from historical_geo.backends.xtent_backend import compile_xtent_solver_input
from historical_geo.compiler import compile_reconstruction_request


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases/crusader_states/public"
ROUND_00 = CASE / "research/rounds/00-initial"
ROUND_01 = CASE / "research/rounds/01-evidence-update"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_sha256(path: Path) -> str:
    payload = json.dumps(
        _load(path), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def test_round_delta_hashes_resolve_to_frozen_before_and_current_after_state() -> None:
    delta = _load(ROUND_01 / "round-delta.json")
    state_changes = _load(ROUND_01 / "state-changes.json")

    before_bundle = _canonical_sha256(ROUND_00 / "research-bundle.snapshot.json")
    after_bundle = _canonical_sha256(CASE / "research-bundle.json")
    before_scenarios = _canonical_sha256(ROUND_00 / "research-scenarios.snapshot.json")
    after_scenarios = _canonical_sha256(CASE / "research-scenarios.json")

    assert delta["bundle_hashes"] == {
        "round_00_canonical_sha256": before_bundle,
        "round_01_canonical_sha256": after_bundle,
    }
    assert delta["scenario_hashes"] == {
        "round_00_canonical_sha256": before_scenarios,
        "round_01_canonical_sha256": after_scenarios,
    }
    assert state_changes["bundle_hashes"] == {
        "before_sha256": before_bundle,
        "after_sha256": after_bundle,
    }
    assert "canonical JSON" in delta["hash_method"]
    assert state_changes["hash_method"] == delta["hash_method"]


def test_round_00_snapshots_are_identified_as_the_same_case() -> None:
    bundle = _load(ROUND_00 / "research-bundle.snapshot.json")
    scenarios = _load(ROUND_00 / "research-scenarios.snapshot.json")
    assert bundle["case_id"] == scenarios["case_id"] == "crusader-states-public-case"


def test_round_00_snapshot_reproduces_the_frozen_v01_reviewed_baseline() -> None:
    bundle = _load(ROUND_00 / "research-bundle.snapshot.json")
    scenarios = _load(ROUND_00 / "research-scenarios.snapshot.json")
    grid = _load(CASE / "case.json")["grid"]
    raw_profile = scenarios["scenarios"]["reviewed-baseline"]

    for slice_value in (1130, 1187):
        profile = {
            key: value.get(str(slice_value), [])
            if key in {"included_decision_ids", "excluded_decision_ids", "changed_decision_ids"}
            and isinstance(value, dict)
            else value
            for key, value in raw_profile.items()
        }
        compiled = compile_xtent_solver_input(
            compile_reconstruction_request(bundle, slice_value, profile, grid)
        )
        assert compiled == build_solver_input(
            CASE, slice_value, scenario="reviewed-baseline"
        )
