"""Fail-closed source-structure screening; no case, compiler or backend writes.

Counts are derived from logged records. Historical qualification and lineage
independence still require source criticism; missing checks never imply GO.
"""

from __future__ import annotations

from typing import Any, Mapping


BUDGET_LIMITS = {
    "queries": 8,
    "content_record_checks": 6,
    "preliminary_sources": 6,
    "held_out_metadata_queries": 2,
    "held_out_candidates": 2,
}
REVIEW_GATES = ("stable_temporal_phase", "spatial_model_fit", "no_dynamic_dependency")
POLITICAL_SOURCE_ROLES = frozenset({
    "political_letter", "historical_chronicle", "translation_same_chronicle",
    "political_archive_record", "explicit_political_inscription",
})


def _index(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    ids = [record[key] for record in records]
    if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise ValueError(f"{key} must be nonempty and unique")
    return dict(zip(ids, records))


def assess_source_structure_preflight(document: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute eligibility, not historical truth, from a complete audit ledger.

    Metadata searches count toward the total query budget. Full-text access is
    measured over all preliminary source records, including failed requests;
    abstracts, excerpts, catalog pages and indexed snippets cannot inflate it.
    """
    candidates = _index(document["candidates"], "candidate_id")
    if document["limits"] != BUDGET_LIMITS:
        raise ValueError("preflight limits cannot be silently changed")
    preferred = document["preferred_if_both_pass"]
    if len(candidates) != 2 or preferred not in candidates:
        raise ValueError("exactly two candidates and a registered preference are required")
    results = {}
    for candidate_id, candidate in candidates.items():
        queries = _index(candidate["query_log"], "query_id")
        checks = _index(candidate["content_record_check_log"], "check_id")
        sources = _index(candidate["preliminary_sources"], "source_id")
        comparators = _index(candidate["held_out_candidates"], "reference_id")
        centers = _index(candidate["centers"], "entity_id")
        rows = _index(candidate["source_matrix"], "row_id")
        for check in checks.values():
            if check["source_id"] not in sources:
                raise ValueError("content check references an unknown source")
        for row in rows.values():
            if row["source_id"] not in sources or row["entity"] not in centers:
                raise ValueError("matrix row references an unknown source or entity")
            source = sources[row["source_id"]]
            if row["source_lineage"] != source["lineage_id"] or row["rights"] != source["rights"]:
                raise ValueError("matrix lineage and rights must match the source record")

        consumed = {
            "queries": len(queries),
            "content_record_checks": len(checks),
            "preliminary_sources": len(sources),
            "held_out_metadata_queries": sum(q["kind"] == "held_out_metadata" for q in queries.values()),
            "held_out_candidates": len(comparators),
        }
        if any(q["kind"] not in {"research", "held_out_metadata"} for q in queries.values()):
            raise ValueError("unknown query kind")
        accessible = {
            check["source_id"] for check in checks.values()
            if check["result"] == "full_text" and check["lawful_access_verified"] is True
        }
        usable = [row for row in rows.values() if row["political_relation"] is True
                  and row["temporal_applicability"] == "candidate_phase"
                  and row["content_observed"] is True]
        relations = {
            entity: sorted({row["locality"] for row in usable if row["entity"] == entity})
            for entity in centers
        }
        lineages = {
            entity: sorted({row["source_lineage"] for row in usable if row["entity"] == entity
                            and sources[row["source_id"]]["evidence_role"] in POLITICAL_SOURCE_ROLES
                            and sources[row["source_id"]]["independence_verified"] is True})
            for entity in centers
        }
        localities = _index(candidate["locality_register"], "locality_id")
        locatable = [place for place in localities.values() if place["identification_verified"] is True
                     and place["locator"] and place["source_id"] in sources]
        exclusions = _index(candidate["conflicts_or_exclusions"], "exclusion_id")
        if any(not item["row_ids"] or set(item["row_ids"]) - rows.keys() for item in exclusions.values()):
            raise ValueError("exclusion must reference observed matrix rows")
        gates = {
            "budget_compliant": all(consumed[key] <= limit for key, limit in BUDGET_LIMITS.items()),
            "two_political_centers": len(centers) >= 2 and all(c["center_verified"] is True for c in centers.values()),
            "four_named_relations_per_center": bool(relations) and all(len(value) >= 4 for value in relations.values()),
            "two_independent_lineages_per_center": bool(lineages) and all(len(value) >= 2 for value in lineages.values()),
            "twelve_locatable_localities": len(locatable) >= 12,
            "legal_text_access_70_percent": bool(sources) and len(accessible) * 10 >= len(sources) * 7,
            "two_conflicts_or_exclusions": len(exclusions) >= 2,
            "comparator_ten_units": any(
                c["metadata_only"] is True and c["excluded"] is False and c["contamination"] is False
                and c["ten_unit_expectation_supported"] is True for c in comparators.values()
            ),
            "isolation_review": candidate["isolation_review"]["status"] == "pass"
            and all(check.get("map_body_selected") is False for check in checks.values()),
        }
        for name in REVIEW_GATES:
            review = candidate["review_gates"].get(name, {})
            gates[name] = review.get("status") == "pass" and bool(review.get("rationale"))
        results[candidate_id] = {
            "decision": "GO" if all(gates.values()) else "NO-GO",
            "budget_consumed": consumed,
            "full_text_access": {"numerator": len(accessible), "denominator": len(sources)},
            "potential_localities_per_center": relations,
            "independent_political_lineages_per_center": lineages,
            "verified_locatable_localities": len(locatable),
            "gates": gates,
        }
    passing = [key for key, value in results.items() if value["decision"] == "GO"]
    selected = preferred if preferred in passing else next(iter(passing), None)
    return {"candidates": results, "selected_candidate_id": selected,
            "decision": "GO" if selected else "NO-GO"}
