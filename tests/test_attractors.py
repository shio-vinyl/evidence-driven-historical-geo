from __future__ import annotations

from shapely.geometry import LineString, box

from historical_geo.attractors import align_shared_boundary


def coverage():
    return {"West": box(0, 0, 5, 6), "East": box(5, 0, 10, 6)}


def test_near_parallel_candidate_preserves_shared_coverage() -> None:
    before = coverage()
    result = align_shared_boundary(before, LineString([(5.2, -1), (5.2, 7)]), max_distance=0.5, max_area_change=0.1)
    assert result.accepted
    assert result.reason == "accepted"
    assert result.direction_similarity == 1.0
    assert result.geometries["West"].intersection(result.geometries["East"]).area == 0
    assert result.geometries["West"].union(result.geometries["East"]).symmetric_difference(box(0, 0, 10, 6)).area == 0


def test_far_candidate_is_rejected_without_geometry_change() -> None:
    before = coverage()
    result = align_shared_boundary(before, LineString([(7, -1), (7, 7)]), max_distance=0.5)
    assert not result.accepted
    assert result.reason == "too_far"
    assert result.geometries == before


def test_excessive_area_change_is_rejected() -> None:
    result = align_shared_boundary(coverage(), LineString([(5.4, -1), (5.4, 7)]), max_distance=0.5, max_area_change=0.05)
    assert not result.accepted
    assert result.reason == "excessive_area_change"
