"""Turn controlled scenario differences into evidence search targets.

The input is deliberately made of ordinary dictionaries.  This keeps the
diagnosis usable before (and independently of) the research contract layer.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


_AXES = ("evidence", "model")


def _identifier_list(value: Any, path: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{path} must be a list of decision IDs")
    result = tuple(value)
    if any(not isinstance(item, str) or not item.strip() for item in result):
        raise ValueError(f"{path} must contain non-empty string decision IDs")
    if len(set(result)) != len(result):
        raise ValueError(f"{path} must not contain duplicate decision IDs")
    return result


def _scenario_definitions(config: Mapping[str, Any]) -> tuple[str, dict[str, dict[str, Any]]]:
    baseline = config.get("baseline")
    scenarios = config.get("scenarios")
    if not isinstance(baseline, str) or not baseline.strip():
        raise ValueError("scenario_config.baseline must name the baseline scenario")
    if not isinstance(scenarios, Mapping):
        raise ValueError("scenario_config.scenarios must be a mapping")
    declared_baselines = [
        name
        for name, raw in scenarios.items()
        if isinstance(raw, Mapping) and raw.get("axis") == "baseline"
    ]
    if declared_baselines and declared_baselines != [baseline]:
        raise ValueError(
            f"scenario_config.baseline {baseline!r} does not match the declared baseline scenario"
        )

    variants: dict[str, dict[str, Any]] = {}
    axis_counts = {axis: 0 for axis in _AXES}
    for name, raw in scenarios.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("scenario names must be non-empty strings")
        if not isinstance(raw, Mapping):
            raise ValueError(f"scenario_config.scenarios.{name} must be a mapping")
        if name == baseline:
            # A baseline entry is optional.  Existing scenario manifests include
            # one with axis="baseline", while the diagnostic variants use the
            # two causal axes below.
            if raw.get("axis", "baseline") != "baseline":
                raise ValueError(f"baseline scenario {name!r} cannot be an evidence or model variant")
            continue
        axis = raw.get("axis")
        if axis not in _AXES:
            raise ValueError(f"scenario {name!r} axis must be 'evidence' or 'model'")
        changed_ids = _identifier_list(
            raw.get("changed_decision_ids"),
            f"scenario_config.scenarios.{name}.changed_decision_ids",
        )
        if not changed_ids:
            raise ValueError(f"scenario {name!r} must name at least one changed decision ID")
        variants[name] = {"axis": axis, "changed_decision_ids": changed_ids}
        axis_counts[axis] += 1

    for axis, count in axis_counts.items():
        if not count:
            raise ValueError(f"scenario_config requires at least one {axis} variant")
    return baseline, variants


def _assignment(value: Any, path: str) -> np.ndarray:
    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{path} must be a rectangular integer assignment array") from exc
    if not array.ndim or not array.size:
        raise ValueError(f"{path} must be a non-empty assignment array")
    if not np.issubdtype(array.dtype, np.integer):
        raise ValueError(f"{path} must contain only integers")
    return array


def _gap_records(evidence_gaps: Any) -> list[Mapping[str, Any]]:
    if isinstance(evidence_gaps, (str, bytes)) or not isinstance(evidence_gaps, Sequence):
        raise ValueError("evidence_gaps must be a list")
    records: list[Mapping[str, Any]] = []
    seen: set[str] = set()
    for index, gap in enumerate(evidence_gaps):
        path = f"evidence_gaps[{index}]"
        if not isinstance(gap, Mapping):
            raise ValueError(f"{path} must be a mapping")
        gap_id = gap.get("gap_id")
        if not isinstance(gap_id, str) or not gap_id.strip():
            raise ValueError(f"{path}.gap_id must be a non-empty string")
        if gap_id in seen:
            raise ValueError(f"duplicate evidence gap ID: {gap_id}")
        seen.add(gap_id)
        if gap.get("status") not in {"open", "closed", "deferred"}:
            raise ValueError(f"{path}.status must be open, closed, or deferred")
        _identifier_list(gap.get("related_decision_ids"), f"{path}.related_decision_ids")
        records.append(gap)
    return records


def _target_text(gap: Mapping[str, Any], field: str) -> str:
    value = gap.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"open evidence gap {gap['gap_id']!r} requires {field}")
    return value


def _preferred_source_types(gap: Mapping[str, Any]) -> list[str]:
    value = gap.get("preferred_source_types")
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(
            f"open evidence gap {gap['gap_id']!r} requires preferred_source_types as a list"
        )
    result = list(value)
    if not result or any(not isinstance(item, str) or not item.strip() for item in result):
        raise ValueError(
            f"open evidence gap {gap['gap_id']!r} requires non-empty preferred_source_types"
        )
    if len(set(result)) != len(result):
        raise ValueError(f"open evidence gap {gap['gap_id']!r} has duplicate preferred_source_types")
    return result


def _slice_sort_key(value: Any) -> tuple[str, str]:
    return type(value).__name__, str(value)


def diagnose_uncertainty(
    scenario_config: Mapping[str, Any],
    assignments: Mapping[Any, Mapping[str, Any]],
    evidence_gaps: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Diagnose scenario sensitivity and create justified historical searches.

    ``assignments`` is keyed first by slice and then by scenario name.  Every
    value is an integer NumPy array or rectangular nested list on the same
    analysis grid.  Slices with no difference from the baseline are omitted.

    A search target can be produced only from an open gap linked to a decision
    changed by an *evidence* scenario.  Thus even a model decision mentioned by
    an EvidenceGap cannot turn pure model sensitivity into a source search.
    """
    if not isinstance(scenario_config, Mapping):
        raise ValueError("scenario_config must be a mapping")
    baseline_name, variants = _scenario_definitions(scenario_config)
    if not isinstance(assignments, Mapping) or not assignments:
        raise ValueError("assignments must be a non-empty slice mapping")
    gaps = _gap_records(evidence_gaps)

    expected_names = {baseline_name, *variants}
    slices: list[dict[str, Any]] = []
    # Attribution retains per-scenario masks, so a gap gets only the cells
    # affected by evidence scenarios that actually mention its decisions.
    evidence_effects: dict[str, list[tuple[Any, np.ndarray]]] = {}
    analysis_shape: tuple[int, ...] | None = None

    for slice_id in sorted(assignments, key=_slice_sort_key):
        raw_slice = assignments[slice_id]
        if not isinstance(raw_slice, Mapping):
            raise ValueError(f"assignments[{slice_id!r}] must be a scenario mapping")
        actual_names = set(raw_slice)
        if actual_names != expected_names:
            missing = sorted(expected_names - actual_names, key=str)
            extra = sorted(actual_names - expected_names, key=str)
            raise ValueError(
                f"assignments[{slice_id!r}] scenarios do not match config; "
                f"missing={missing}, extra={extra}"
            )

        baseline = _assignment(raw_slice[baseline_name], f"assignments[{slice_id!r}].{baseline_name}")
        if analysis_shape is None:
            analysis_shape = baseline.shape
        elif baseline.shape != analysis_shape:
            raise ValueError(
                f"assignment shape mismatch in slice {slice_id!r}: "
                f"baseline has {baseline.shape}, analysis grid has {analysis_shape}"
            )
        masks: dict[str, dict[str, np.ndarray]] = {axis: {} for axis in _AXES}
        for name in sorted(variants):
            current = _assignment(raw_slice[name], f"assignments[{slice_id!r}].{name}")
            if current.shape != baseline.shape:
                raise ValueError(
                    f"assignment shape mismatch in slice {slice_id!r}: "
                    f"{name} has {current.shape}, baseline has {baseline.shape}"
                )
            difference = current != baseline
            if difference.any():
                axis = variants[name]["axis"]
                masks[axis][name] = difference
                if axis == "evidence":
                    evidence_effects.setdefault(name, []).append((slice_id, difference))

        if not masks["evidence"] and not masks["model"]:
            continue
        axis_union = {
            axis: np.logical_or.reduce(tuple(axis_masks.values()))
            if axis_masks
            else np.zeros(baseline.shape, dtype=bool)
            for axis, axis_masks in masks.items()
        }
        evidence_changed = bool(masks["evidence"])
        model_changed = bool(masks["model"])
        classification = (
            "mixed" if evidence_changed and model_changed
            else "evidence_gap" if evidence_changed
            else "model_sensitivity"
        )
        changed_ids = {
            axis: sorted(
                {
                    decision_id
                    for name in masks[axis]
                    for decision_id in variants[name]["changed_decision_ids"]
                }
            )
            for axis in _AXES
        }
        total_mask = axis_union["evidence"] | axis_union["model"]
        slices.append(
            {
                "slice": slice_id,
                "classification": classification,
                "affected_grid_cells": {
                    "evidence": int(axis_union["evidence"].sum()),
                    "model": int(axis_union["model"].sum()),
                    "total": int(total_mask.sum()),
                },
                "changed_scenarios": {
                    axis: sorted(masks[axis]) for axis in _AXES
                },
                "changed_decision_ids": {
                    **changed_ids,
                    "all": sorted(set(changed_ids["evidence"]) | set(changed_ids["model"])),
                },
            }
        )

    targets: list[dict[str, Any]] = []
    for gap in gaps:
        if gap["status"] != "open":
            continue
        related_ids = set(gap["related_decision_ids"])
        matching_scenarios = [
            name
            for name, definition in variants.items()
            if definition["axis"] == "evidence"
            and related_ids.intersection(definition["changed_decision_ids"])
            and name in evidence_effects
        ]
        if not matching_scenarios:
            continue

        impacted_by_slice: dict[Any, np.ndarray] = {}
        linked_ids: set[str] = set()
        for name in matching_scenarios:
            linked_ids.update(related_ids.intersection(variants[name]["changed_decision_ids"]))
            for slice_id, mask in evidence_effects[name]:
                if slice_id in impacted_by_slice:
                    impacted_by_slice[slice_id] |= mask
                else:
                    impacted_by_slice[slice_id] = mask.copy()
        impacted_cells = sum(int(mask.sum()) for mask in impacted_by_slice.values())
        targets.append(
            {
                "gap_id": gap["gap_id"],
                "question": _target_text(gap, "question"),
                "preferred_source_types": _preferred_source_types(gap),
                "success_criteria": _target_text(gap, "success_criteria"),
                "stop_condition": _target_text(gap, "stop_condition"),
                "priority_basis": {
                    "affected_grid_cells": impacted_cells,
                    "related_decision_count": len(linked_ids),
                    "related_decision_ids": sorted(linked_ids),
                    "slices": sorted(impacted_by_slice, key=_slice_sort_key),
                },
            }
        )

    # Larger observed spatial effects sort first, then broader explicit
    # decision linkage.  gap_id is the stable tie-breaker.  These are counts,
    # not probabilities or confidence estimates.
    targets.sort(
        key=lambda target: (
            -target["priority_basis"]["affected_grid_cells"],
            -target["priority_basis"]["related_decision_count"],
            target["gap_id"],
        )
    )
    return {"slices": slices, "search_targets": targets}


def build_diagnosis_documents(
    case_id: str,
    scenario_config: Mapping[str, Any],
    assignments: Mapping[Any, Mapping[str, Any]],
    evidence_gaps: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build schema-valid diagnosis and ranked search-target documents."""
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string")
    baseline = scenario_config.get("baseline")
    raw = diagnose_uncertainty(scenario_config, assignments, evidence_gaps)
    gaps_by_id = {gap["gap_id"]: gap for gap in evidence_gaps}
    formal_targets = []
    for target in raw["search_targets"]:
        gap = gaps_by_id[target["gap_id"]]
        formal_targets.append(
            {
                "target_id": f"TARGET_{target['gap_id']}",
                "evidence_gap_ids": [target["gap_id"]],
                "claim_ids": sorted(gap.get("related_claim_ids", [])),
                "decision_ids": list(target["priority_basis"]["related_decision_ids"]),
                "question": target["question"],
                "preferred_source_types": target["preferred_source_types"],
                "success_criteria": target["success_criteria"],
                "stop_condition": target["stop_condition"],
                "priority_basis": target["priority_basis"],
                "status": "open",
            }
        )
    diagnosis_document = {
        "contract_version": "historical_geo.uncertainty_diagnosis.v0.2",
        "case_id": case_id,
        "baseline_scenario": baseline,
        "slices": raw["slices"],
    }
    targets_document = {
        "contract_version": "historical_geo.search_targets.v0.2",
        "case_id": case_id,
        "targets": formal_targets,
    }
    return diagnosis_document, targets_document


# A descriptive alias for callers that name the scenario step explicitly.
diagnose_scenario_uncertainty = diagnose_uncertainty
