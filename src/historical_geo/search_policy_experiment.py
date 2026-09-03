"""Deterministic, equal-budget replay of evidence-search policies.

The replay consumes a real search-target document but never presents constructed
retrieval outcomes as historical research.  Its narrow purpose is to test policy
selection and metric accounting before comparable live search traces exist.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator


SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
CONFIG_SCHEMA = SCHEMA_DIR / "search-policy-experiment.schema.json"
RESULT_SCHEMA = SCHEMA_DIR / "search-policy-experiment-result.schema.json"


class PolicyExperimentError(ValueError):
    """Raised when a replay input violates cross-document experiment rules."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PolicyExperimentError(f"{path} must contain a JSON object")
    return value


def canonical_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(encoded).hexdigest()


def _schema_errors(instance: Mapping[str, Any], schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    return [
        f"{'.'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: tuple(map(str, item.absolute_path)))
    ]


def _require_schema(instance: Mapping[str, Any], schema_path: Path) -> None:
    errors = _schema_errors(instance, schema_path)
    if errors:
        raise PolicyExperimentError("; ".join(errors))


def _cell_key(slice_value: Any, index: int) -> tuple[str, int]:
    # JSON encoding prevents integer 1130 and string "1130" from silently colliding.
    return json.dumps(slice_value, sort_keys=True, ensure_ascii=False), index


def _expand_ranges(ranges: Iterable[Mapping[str, Any]]) -> set[tuple[str, int]]:
    cells: set[tuple[str, int]] = set()
    for item in ranges:
        start = int(item["start"])
        end = int(item["end_exclusive"])
        if end <= start:
            raise PolicyExperimentError(f"cell range end_exclusive must exceed start: {dict(item)}")
        cells.update(_cell_key(item["slice"], index) for index in range(start, end))
    return cells


def _open_targets(search_targets: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    targets = search_targets.get("targets")
    if not isinstance(targets, list):
        raise PolicyExperimentError("search target document must contain a targets array")
    open_targets = [target for target in targets if target.get("status") == "open"]
    if not open_targets:
        raise PolicyExperimentError("search target document has no open targets")
    ids = [str(target.get("target_id")) for target in open_targets]
    if len(ids) != len(set(ids)):
        raise PolicyExperimentError("open search target IDs must be unique")
    return open_targets


def _validate_cross_document_rules(
    config: Mapping[str, Any], search_targets: Mapping[str, Any]
) -> tuple[list[Mapping[str, Any]], dict[str, Mapping[str, Any]], set[tuple[str, int]]]:
    if config["case_id"] != search_targets.get("case_id"):
        raise PolicyExperimentError("experiment and search-target case_id values differ")

    targets = _open_targets(search_targets)
    target_index = {str(target["target_id"]): target for target in targets}
    target_ids = set(target_index)
    budget = int(config["evidence_budget"])
    if budget > len(targets):
        raise PolicyExperimentError("evidence budget exceeds the number of open targets")

    policies = config["policies"]
    policy_ids = [policy["policy_id"] for policy in policies]
    if set(policy_ids) != {"targeted", "fixed", "broad"} or len(policy_ids) != 3:
        raise PolicyExperimentError("policies must contain targeted, fixed, and broad exactly once")
    for policy in policies:
        if policy["policy_id"] == "targeted":
            continue
        declared = policy["target_order"]
        if set(declared) != target_ids or len(declared) != len(target_ids):
            raise PolicyExperimentError(
                f"{policy['policy_id']} target_order must be a permutation of every open target"
            )

    outcomes = config["fixture_outcomes"]
    outcome_ids = [outcome["target_id"] for outcome in outcomes]
    if set(outcome_ids) != target_ids or len(outcome_ids) != len(target_ids):
        raise PolicyExperimentError("fixture outcomes must cover every open target exactly once")

    initial_cells = _expand_ranges(config["initial_evidence_sensitive_cell_ranges"])
    if not initial_cells:
        raise PolicyExperimentError("initial evidence-sensitive cell universe is empty")

    outcome_index: dict[str, Mapping[str, Any]] = {}
    for outcome in outcomes:
        target_id = outcome["target_id"]
        target = target_index[target_id]
        closed = set(outcome["closed_gap_ids"])
        allowed_gaps = set(target.get("evidence_gap_ids", []))
        if not closed <= allowed_gaps:
            raise PolicyExperimentError(f"{target_id} closes a gap outside its search target")
        affected = _expand_ranges(outcome["affected_cell_ranges"])
        resolved = _expand_ranges(outcome["resolved_sensitive_cell_ranges"])
        if not affected <= initial_cells:
            raise PolicyExperimentError(f"{target_id} affects cells outside the declared initial universe")
        if not resolved <= affected:
            raise PolicyExperimentError(f"{target_id} resolves cells it does not affect")
        outcome_index[target_id] = outcome

    return targets, outcome_index, initial_cells


def _selection_order(policy: Mapping[str, Any], targets: list[Mapping[str, Any]]) -> list[str]:
    if policy["policy_id"] != "targeted":
        return list(policy["target_order"])
    indexed = list(enumerate(targets))
    ranked = sorted(
        indexed,
        key=lambda item: (
            -int(item[1]["priority_basis"]["affected_grid_cells"]),
            item[0],
        ),
    )
    return [str(target["target_id"]) for _, target in ranked]


def run_policy_experiment(
    config: Mapping[str, Any], search_targets: Mapping[str, Any]
) -> dict[str, Any]:
    """Run a deterministic replay under one equal retrieval budget.

    ``fixture_outcomes`` are deliberately counterfactual inputs.  This function
    measures only what follows from those declared outcomes and never infers that
    any retrieval or historical finding actually occurred.
    """

    _require_schema(config, CONFIG_SCHEMA)
    targets, outcomes, initial_cells = _validate_cross_document_rules(config, search_targets)
    budget = int(config["evidence_budget"])
    policy_results: list[dict[str, Any]] = []

    for policy in config["policies"]:
        selected_ids = _selection_order(policy, targets)[:budget]
        affected_union: set[tuple[str, int]] = set()
        resolved_union: set[tuple[str, int]] = set()
        closed_gaps: set[str] = set()
        retrievals: list[dict[str, Any]] = []

        for index, target_id in enumerate(selected_ids, start=1):
            outcome = outcomes[target_id]
            affected = _expand_ranges(outcome["affected_cell_ranges"])
            resolved = _expand_ranges(outcome["resolved_sensitive_cell_ranges"])
            new_affected = affected - affected_union
            new_resolved = resolved - resolved_union
            affected_union.update(affected)
            resolved_union.update(resolved)
            closed_gaps.update(outcome["closed_gap_ids"])
            retrievals.append(
                {
                    "index": index,
                    "target_id": target_id,
                    "closed_gap_ids": list(outcome["closed_gap_ids"]),
                    "newly_affected_grid_cells": len(new_affected),
                    "newly_resolved_sensitive_cells": len(new_resolved),
                }
            )

        policy_results.append(
            {
                "policy_id": policy["policy_id"],
                "selected_target_ids": selected_ids,
                "retrievals": retrievals,
                "metrics": {
                    "gaps_closed_per_retrieval": round(len(closed_gaps) / budget, 6),
                    "new_evidence_affected_grid_cells": len(affected_union),
                    "remaining_evidence_sensitive_cells": len(initial_cells - resolved_union),
                },
            }
        )

    result = {
        "contract_version": "historical_geo.search_policy_experiment_result.v0.1",
        "case_id": config["case_id"],
        "evaluation_mode": config["evaluation_mode"],
        "evidence_budget": budget,
        "provenance": {
            "experiment_sha256": canonical_sha256(config),
            "search_targets_sha256": canonical_sha256(search_targets),
        },
        "initial_evidence_sensitive_cells": len(initial_cells),
        "policy_results": policy_results,
        "interpretation": (
            "This result compares policy mechanics under the declared fixture only. "
            "It is not evidence that any policy improves real historical research."
        ),
        "limitations": list(config["limitations"]),
    }
    _require_schema(result, RESULT_SCHEMA)
    return result


def run_policy_experiment_files(config_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    """Load an experiment and its referenced target document, then optionally write the result."""

    config = load_json(config_path)
    target_path = (config_path.parent / config["search_targets_path"]).resolve()
    search_targets = load_json(target_path)
    result = run_policy_experiment(config, search_targets)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
