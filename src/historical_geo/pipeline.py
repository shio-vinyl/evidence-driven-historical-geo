"""Minimum deterministic reconstruction and audit path."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
from rasterio.transform import rowcol
from pyproj import Transformer
from shapely import union_all
from shapely.geometry import GeometryCollection, mapping, shape
from shapely.ops import transform as transform_geometry

from historical_geo import xtent
from historical_geo.adapter import _schema_dir, build_solver_input, load_case, normalize_scenario
from historical_geo.contracts import CALIBRATION_VERSION, RUN_VERSION, validate_schema


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_feature_collection(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"{path} must be a GeoJSON FeatureCollection")
    return list(data.get("features", []))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _geometry_to_grid_crs(geometry: Any, grid_crs: str) -> Any:
    """Transform GeoJSON fixture geometry (WGS84) into the solver grid CRS."""
    if str(grid_crs).upper() in {"EPSG:4326", "WGS84"}:
        return geometry
    transformer = Transformer.from_crs("EPSG:4326", grid_crs, always_xy=True)
    return transform_geometry(transformer.transform, geometry)


def _coordinates_to_grid(longitude: float, latitude: float, grid_crs: str) -> tuple[float, float]:
    """Transform a reviewed WGS84 seed coordinate into the solver grid CRS."""
    if str(grid_crs).upper() in {"EPSG:4326", "WGS84"}:
        return longitude, latitude
    transformer = Transformer.from_crs("EPSG:4326", grid_crs, always_xy=True)
    return transformer.transform(longitude, latitude)


def _nearest_land_cell(land_mask: np.ndarray, row: int, col: int, max_radius: int = 3) -> tuple[int, int]:
    """Keep approximate coastal gazetteer points on the nearest modeled land cell."""
    if land_mask[row, col]:
        return row, col
    height, width = land_mask.shape
    candidates: list[tuple[int, int, int]] = []
    for radius in range(1, max_radius + 1):
        r0, r1 = max(0, row - radius), min(height, row + radius + 1)
        c0, c1 = max(0, col - radius), min(width, col + radius + 1)
        for r in range(r0, r1):
            for c in range(c0, c1):
                if land_mask[r, c]:
                    candidates.append(((r - row) ** 2 + (c - col) ** 2, r, c))
        if candidates:
            _, nearest_row, nearest_col = min(candidates)
            return nearest_row, nearest_col
    raise ValueError(f"seed cell is water and no land cell lies within {max_radius} cells: {(row, col)}")


def _remove_reprojection_overlaps(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Restore exclusive coverage after nonlinear CRS transformation of shared edges."""
    occupied: Any = GeometryCollection()
    rows = []
    for _, row in gdf.sort_values("entity").iterrows():
        cleaned = row.geometry.difference(occupied)
        if not cleaned.is_empty:
            copied = row.copy()
            copied.geometry = cleaned
            rows.append(copied)
            occupied = union_all([occupied, cleaned])
    return gpd.GeoDataFrame(rows, columns=gdf.columns, crs=gdf.crs)


def _enforce_seed_ownership(
    label: np.ndarray, entities: list[str], seeds_by_entity: dict[str, list[tuple[int, int, float]]]
) -> np.ndarray:
    """Guarantee that every reviewed point-control anchor owns its raster cell."""
    out = label.copy()
    occupied: dict[tuple[int, int], str] = {}
    for entity_index, entity in enumerate(entities, start=1):
        for row, col, _ in seeds_by_entity[entity]:
            key = (row, col)
            if key in occupied and occupied[key] != entity:
                raise ValueError(f"conflicting reviewed seeds share cell {key}: {occupied[key]} and {entity}")
            occupied[key] = entity
            out[row, col] = entity_index
    return out


def _active_phase_by_entity(solver_input: dict[str, Any]) -> dict[str, dict[str, Any]]:
    phases: dict[str, dict[str, Any]] = {}
    for record in solver_input["phases"]:
        entity = record["parameters"]["entity"]
        if entity in phases:
            raise ValueError(f"multiple active phases for {entity}")
        phases[entity] = record
    return phases


def run_directory(case_dir: Path, slice_value: int | str, scenario: str = "reviewed-baseline") -> Path:
    normalized = normalize_scenario(scenario)
    suffix = "" if normalized == "reviewed-baseline" else f"-{normalized}"
    return case_dir.resolve() / "build" / f"run-{slice_value}{suffix}"


def reconstruct(case_dir: Path, slice_value: int | str, *, scenario: str = "reviewed-baseline") -> Path:
    case_dir = case_dir.resolve()
    solver_input = build_solver_input(case_dir, slice_value, scenario=scenario)
    return reconstruct_solver_input(case_dir, solver_input)


def reconstruct_solver_input(case_dir: Path, solver_input: dict[str, Any]) -> Path:
    """Run XTENT from an already compiled and validated solver-input document."""
    case_dir = case_dir.resolve()
    case = load_case(case_dir)
    errors = validate_schema(solver_input, _schema_dir() / "solver-input.schema.json")
    if errors:
        raise ValueError("; ".join(f"{x.path}: {x.message}" for x in errors))
    slice_value = solver_input["slice"]
    scenario = solver_input["scenario"]
    grid_cfg = solver_input["grid"]
    grid = xtent.build_grid(tuple(grid_cfg["bbox"]), float(grid_cfg["resolution"]), str(grid_cfg["crs"]))

    land_path = case_dir / grid_cfg["land_path"]
    natural_path = case_dir / grid_cfg["natural_features_path"]
    land_features = _read_feature_collection(land_path)
    if not land_features:
        raise ValueError("land fixture has no features")
    land = union_all([_geometry_to_grid_crs(shape(x["geometry"]), grid.crs) for x in land_features])

    natural_features = _read_feature_collection(natural_path)
    natural_by_id = {x.get("properties", {}).get("feature_id"): x for x in natural_features}
    barriers = []
    for record in solver_input["barriers"]:
        params = record["parameters"]
        feature_id = params["feature_id"]
        feature = natural_by_id.get(feature_id)
        if not feature:
            raise ValueError(f"natural feature not found: {feature_id}")
        barriers.append((_geometry_to_grid_crs(shape(feature["geometry"]), grid.crs), xtent.barrier_cost(params["strength"])))

    sea_cost = xtent.sea_cost_for_profile(grid_cfg["friction_profile"])
    friction, land_mask = xtent.build_friction(grid, land, barriers, sea_cost=sea_cost)

    phases = _active_phase_by_entity(solver_input)
    entities = sorted(phases)
    seeds_by_entity: dict[str, list[tuple[int, int, float]]] = {x: [] for x in entities}
    for record in solver_input["seeds"]:
        params = record["parameters"]
        entity = params["entity"]
        if entity not in seeds_by_entity:
            continue
        longitude, latitude = params["coordinates"]
        x, y = _coordinates_to_grid(longitude, latitude, grid.crs)
        row, col = rowcol(grid.transform, x, y)
        if not (0 <= row < grid.height and 0 <= col < grid.width):
            raise ValueError(f"seed outside grid: {params['name']}")
        row, col = _nearest_land_cell(land_mask, int(row), int(col))
        weight = xtent.weight_ordinal(params.get("weight_ordinal", "major"))
        seeds_by_entity[entity].append((row, col, weight))

    fields = []
    for entity in entities:
        if not seeds_by_entity[entity]:
            raise ValueError(f"no active seed for {entity}")
        projection = phases[entity]["parameters"]["projection"]
        fields.append(xtent.influence_field(friction, seeds_by_entity[entity], xtent.projection_k(projection)))
    label, claimed, margin = xtent.allocate(np.stack(fields))
    label = _enforce_seed_ownership(label, entities, seeds_by_entity)
    label[~land_mask] = 0

    gdf = xtent.vectorize(label, grid.transform, entities, crs=grid.crs)
    if grid.crs != "EPSG:4326":
        gdf = _remove_reprojection_overlaps(gdf.to_crs("EPSG:4326"))

    all_barrier_records = solver_input["barriers"]
    feature_rows = []
    for _, row in gdf.sort_values("entity").iterrows():
        entity = str(row["entity"])
        records = [x for x in solver_input["seeds"] if x["parameters"]["entity"] == entity]
        records += [phases[entity], *all_barrier_records]
        decision_ids = sorted({x["decision_id"] for x in records})
        evidence_ids = sorted({value for x in records for value in x["evidence_ids"]})
        source_ids = sorted({value for x in records for value in x["source_ids"]})
        assumption_heavy = any("assumption_reason" in x for x in records)
        properties = {
            "output_feature_id": f"{case['case_id']}:{slice_value}:{entity.lower().replace(' ', '-')}",
            "entity": entity,
            "slice": slice_value,
            "model_label": "boundary_hypothesis",
            "decision_ids": decision_ids,
            "evidence_ids": evidence_ids,
            "source_ids": source_ids,
            "geometry_adjustment": "none",
            "uncertainty": "assumption-heavy" if assumption_heavy else "modeled",
        }
        errors = validate_schema(properties, _schema_dir() / "output-feature.schema.json")
        if errors:
            raise ValueError("; ".join(f"{x.path}: {x.message}" for x in errors))
        feature_rows.append({"type": "Feature", "properties": properties, "geometry": mapping(row.geometry)})

    run_dir = run_directory(case_dir, slice_value, scenario)
    surface_path = run_dir / "boundary-hypotheses.geojson"
    collection = {
        "type": "FeatureCollection",
        "name": "boundary_hypotheses",
        "features": feature_rows,
    }
    _write_json(surface_path, collection)

    audit = audit_surface(surface_path, expected_entities=entities)
    if not all(audit.values()):
        raise ValueError(f"reconstruction audit failed: {audit}")
    effective_path = run_dir / "effective-solver-input.json"
    _write_json(effective_path, solver_input)
    manifest = {
        "contract_version": RUN_VERSION,
        "run_id": f"{case['case_id']}-{slice_value}-{scenario}-minimum",
        "case_id": case["case_id"],
        "slice": slice_value,
        "scenario": scenario,
        "calibration_version": CALIBRATION_VERSION,
        "effective_input_sha256": _sha256(effective_path),
        "outputs": {
            "boundary_hypotheses": {"path": surface_path.name, "sha256": _sha256(surface_path)}
        },
        "entity_counts": {"expected": len(entities), "materialized": len(feature_rows)},
        "validation": audit,
    }
    errors = validate_schema(manifest, _schema_dir() / "reconstruction-run.schema.json")
    if errors:
        raise ValueError("; ".join(f"{x.path}: {x.message}" for x in errors))
    _write_json(run_dir / "run-manifest.json", manifest)
    return run_dir


def audit_surface(surface_path: Path, expected_entities: list[str] | None = None) -> dict[str, bool]:
    features = _read_feature_collection(surface_path)
    geoms = [shape(x["geometry"]) for x in features]
    entities = [str(x["properties"]["entity"]) for x in features]
    valid = all(not geom.is_empty and geom.is_valid for geom in geoms)
    non_overlapping = True
    for index, geom in enumerate(geoms):
        for other in geoms[index + 1 :]:
            if geom.intersection(other).area > 1e-12:
                non_overlapping = False
    retained = expected_entities is None or sorted(entities) == sorted(expected_entities)
    return {"valid": valid, "non_overlapping": non_overlapping, "entities_retained": retained}
