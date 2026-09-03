"""Guarded post-vector boundary alignment for controlled diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from shapely import union_all
from shapely.geometry import LineString
from shapely.ops import split


@dataclass(frozen=True)
class AlignmentResult:
    accepted: bool
    reason: str
    geometries: dict[str, Any]
    score: float
    distance: float
    direction_similarity: float
    max_area_change: float


def _lines(geometry: Any) -> list[LineString]:
    if geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        return [geometry]
    if hasattr(geometry, "geoms"):
        return [part for geom in geometry.geoms for part in _lines(geom)]
    return []


def _direction(line: LineString) -> tuple[float, float]:
    start, end = line.coords[0], line.coords[-1]
    dx, dy = end[0] - start[0], end[1] - start[1]
    norm = math.hypot(dx, dy)
    return (dx / norm, dy / norm) if norm else (0.0, 0.0)


def align_shared_boundary(
    geometries: dict[str, Any],
    candidate: LineString,
    *,
    max_distance: float,
    min_direction_similarity: float = 0.8,
    max_area_change: float = 0.1,
) -> AlignmentResult:
    """Replace one shared edge only when proximity, direction, area, and topology pass.

    The coverage union is split by the candidate and each resulting face is assigned
    to the entity with the greatest overlap with the pre-alignment geometry. This
    keeps a single shared edge instead of snapping polygons independently.
    """
    if len(geometries) < 2:
        return AlignmentResult(False, "needs_multiple_entities", geometries, 0.0, math.inf, 0.0, 0.0)
    names = sorted(geometries)
    shared_parts = []
    for index, name in enumerate(names):
        for other in names[index + 1 :]:
            shared_parts.extend(_lines(geometries[name].boundary.intersection(geometries[other].boundary)))
    if not shared_parts:
        return AlignmentResult(False, "no_shared_boundary", geometries, 0.0, math.inf, 0.0, 0.0)
    shared = max(shared_parts, key=lambda line: line.length)
    distance = shared.distance(candidate)
    a, b = _direction(shared), _direction(candidate)
    direction = abs(a[0] * b[0] + a[1] * b[1])
    length_ratio = min(shared.length, candidate.length) / max(shared.length, candidate.length)
    distance_score = max(0.0, 1.0 - distance / max_distance) if max_distance > 0 else 0.0
    score = 0.45 * distance_score + 0.35 * direction + 0.20 * length_ratio
    if distance > max_distance:
        return AlignmentResult(False, "too_far", geometries, score, distance, direction, 0.0)
    if direction < min_direction_similarity:
        return AlignmentResult(False, "direction_mismatch", geometries, score, distance, direction, 0.0)

    coverage = union_all(list(geometries.values()))
    pieces = list(split(coverage, candidate).geoms)
    if len(pieces) < len(geometries):
        return AlignmentResult(False, "candidate_does_not_split_coverage", geometries, score, distance, direction, 0.0)

    assigned: dict[str, list[Any]] = {name: [] for name in names}
    for piece in pieces:
        winner = max(names, key=lambda name: piece.intersection(geometries[name]).area)
        assigned[winner].append(piece)
    if any(not assigned[name] for name in names):
        return AlignmentResult(False, "entity_loss", geometries, score, distance, direction, 1.0)
    rebuilt = {name: union_all(assigned[name]) for name in names}
    changes = {
        name: abs(rebuilt[name].area - geometries[name].area) / max(geometries[name].area, 1e-12)
        for name in names
    }
    largest_change = max(changes.values())
    if largest_change > max_area_change:
        return AlignmentResult(False, "excessive_area_change", geometries, score, distance, direction, largest_change)
    if any(not geom.is_valid for geom in rebuilt.values()):
        return AlignmentResult(False, "invalid_geometry", geometries, score, distance, direction, largest_change)
    for index, name in enumerate(names):
        for other in names[index + 1 :]:
            if rebuilt[name].intersection(rebuilt[other]).area > 1e-12:
                return AlignmentResult(False, "overlap", geometries, score, distance, direction, largest_change)
    if coverage.symmetric_difference(union_all(list(rebuilt.values()))).area > 1e-12:
        return AlignmentResult(False, "coverage_changed", geometries, score, distance, direction, largest_change)
    return AlignmentResult(True, "accepted", rebuilt, score, distance, direction, largest_change)
