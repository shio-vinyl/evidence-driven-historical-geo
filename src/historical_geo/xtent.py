"""Cost-distance XTENT territorial allocation: a surface-generation engine.

Pure, testable core ported from the validated Phase-0 prototype
(``scripts/prototype_xtent_field.py``). Builds territory from *seeds + friction +
cost-distance XTENT allocation*.

Two layers stay strictly separate (survey §4):

* **Allocation (honest):** seeds → friction → per-entity XTENT influence field
  ``I = C^a - k·cost`` → thresholded argmax (``allocate``). ``I ≤ 0`` genuinely
  means "no control"; the border falls where two influence fields cross.
* **Cartographic cleanup (presentation):** ridge-bridging gap fill (``cleanup``)
  and seedless-island removal (``remove_orphans``) tidy raster artifacts without
  mutating the underlying allocation.

Agent judgments enter only as **ordinals** (projection ∈ expansive|normal|
contracted, barrier ∈ hard|soft|porous, weight ∈ capital|major|minor|…). The
ordinal→bounded-numeric tables below are the *one* place the otherwise-subjective
XTENT calibration lives — versioned and auditable, never per-map floats.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import numpy as np
import rasterio.features
from rasterio.transform import from_bounds
from skimage.graph import MCP_Geometric

# --- ordinal → bounded numeric calibration (Tier-0 defaults; recipe/agent may
#     override). The agent only ever emits the ordinal keys. -------------------
PROJECTION_K = {"expansive": 0.055, "normal": 0.08, "contracted": 0.12}
WEIGHT_EXPONENT = 1.0  # exponent `a` on center weight (how much size buys reach)

WEIGHT_BY_TYPE = {
    "capital": 4.0, "capital_port": 4.0,
    "port": 2.5, "city": 2.5, "religious_center": 2.5,
    "frontier_city": 2.3, "frontier_town": 2.0,
    "sacred_precinct": 3.0,
    "fortress": 1.6, "castle": 1.6, "frontier_fortress": 1.6, "frontier_castle": 1.5,
    "pass": 1.2, "battlefield_frontier": 1.0,
}
WEIGHT_DEFAULT = 2.0

# center-weight ordinal (model_params seed override vocabulary) → bounded weight.
# Distinct from WEIGHT_BY_TYPE: agents may override a seed's weight by rank when
# the settlement type alone undersells its political role.
WEIGHT_ORDINAL = {"capital": 4.0, "major": 2.5, "minor": 1.6, "outpost": 1.2}

# friction
SEA_COST = 30.0          # settled profile; maritime would lower this
GATE_SEED_TYPES = frozenset({"pass"})
GATE_RADIUS = 7          # cells (~15 km) — bridges a range at a held pass
GATE_COST = 1.5          # carved cost inside the gate notch

# barrier strength ordinal → additive per-cell cost on the feature (plan §4).
BARRIER_STRENGTH = {"hard": 10.0, "soft": 4.0, "porous": 2.0}

# friction profiles: civilization movement models. Only sea cost differs in
# Phase-1 (settled powers fear the sea; maritime ones use it as a highway). Steppe
# tuning for `nomadic` is a later refinement (anisotropy is a Phase-1 non-goal).
FRICTION_PROFILES = {
    "settled": {"sea_cost": 30.0},
    "maritime": {"sea_cost": 6.0},
    "nomadic": {"sea_cost": 30.0},
}

# corridors (tapered route control): a wedge wide at the body, narrowing to a tip
CORRIDOR_W_START = 5.0   # half-width at the body anchor (~11 km)
CORRIDOR_W_END = 0.0     # half-width at the far tip (a point)
# corridor width ordinal → (half-width at body, half-width at tip) in cells
CORRIDOR_WIDTH = {"narrow": (5.0, 0.0), "normal": (8.0, 0.0)}

# presentation cleanup
CLEANUP_FILL_CELLS = 8   # ~18 km: bridges a ridge to its medial line; desert stays
MAX_ORPHAN_CELLS = 1500  # seedless components up to this size are reassigned
CONTEST_MARGIN = 0.30    # top1-top2 influence margin below this reads as contested


@dataclass(frozen=True)
class Grid:
    """A projected raster: affine ``transform``, ``height`` × ``width`` cells."""

    transform: Any
    width: int
    height: int
    bbox: tuple[float, float, float, float]  # (west, south, east, north)
    crs: str

    @property
    def shape(self) -> tuple[int, int]:
        return (self.height, self.width)


# --- ordinal helpers --------------------------------------------------------
def projection_k(projection: str) -> float:
    """Map a projection ordinal to its bounded decay coefficient ``k``."""
    return PROJECTION_K[projection]


def seed_weight(settlement_type: str | None) -> float:
    """Map a settlement type ordinal to its bounded center weight ``C``."""
    return WEIGHT_BY_TYPE.get(settlement_type or "", WEIGHT_DEFAULT)


def weight_ordinal(rank: str) -> float:
    """Map a center-weight rank ordinal (capital|major|minor|outpost) to ``C``."""
    return WEIGHT_ORDINAL[rank]


def barrier_cost(strength: str) -> float:
    """Map a barrier strength ordinal (hard|soft|porous) to its added cost."""
    return BARRIER_STRENGTH[strength]


def sea_cost_for_profile(profile: str) -> float:
    """Sea friction for a civilization movement profile (settled|maritime|nomadic)."""
    return FRICTION_PROFILES[profile]["sea_cost"]


def corridor_width(width: str) -> tuple[float, float]:
    """Map a corridor width ordinal (narrow|normal) to (body, tip) half-widths."""
    return CORRIDOR_WIDTH[width]


# --- grid + rasterization ---------------------------------------------------
def build_grid(
    bbox: tuple[float, float, float, float], res: float, crs: str = "EPSG:4326"
) -> Grid:
    """Build a raster grid from a lon/lat ``bbox`` and cell size.

    For ``EPSG:4326`` the grid is the bbox itself with ``res`` in degrees. For any
    projected ``crs`` (an equal-area CRS in metres is the intended use), the bbox is
    reprojected and ``res`` is the cell size in CRS units — so every cell has the
    same ground area and cost-distance is not stretched toward the poles. ``bbox``
    on the returned grid stays in lon/lat for reference.
    """
    west, south, east, north = bbox
    if str(crs).upper() in ("EPSG:4326", "WGS84"):
        width = int(round((east - west) / res))
        height = int(round((north - south) / res))
        transform = from_bounds(west, south, east, north, width, height)
        return Grid(transform=transform, width=width, height=height, bbox=bbox, crs=crs)

    from pyproj import Transformer

    tf = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    t = np.linspace(0.0, 1.0, 129)
    lons = np.concatenate(
        [
            west + (east - west) * t,
            west + (east - west) * t,
            np.full_like(t, west),
            np.full_like(t, east),
        ]
    )
    lats = np.concatenate(
        [
            np.full_like(t, south),
            np.full_like(t, north),
            south + (north - south) * t,
            south + (north - south) * t,
        ]
    )
    xs, ys = tf.transform(lons, lats)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    width = int(round((maxx - minx) / res))
    height = int(round((maxy - miny) / res))
    transform = from_bounds(minx, miny, maxx, maxy, width, height)
    return Grid(transform=transform, width=width, height=height, bbox=bbox, crs=crs)


def rasterize_geom(grid: Grid, geom: Any, all_touched: bool = False) -> np.ndarray:
    """Burn a single geometry into a boolean mask on ``grid``."""
    if geom is None or getattr(geom, "is_empty", False):
        return np.zeros(grid.shape, dtype=bool)
    return rasterio.features.rasterize(
        [(geom, 1)],
        out_shape=grid.shape,
        transform=grid.transform,
        fill=0,
        all_touched=all_touched,
        dtype="uint8",
    ).astype(bool)


# --- friction surface -------------------------------------------------------
def build_friction(
    grid: Grid,
    land_geom: Any,
    barriers: Iterable[tuple[Any, float]] = (),
    sea_cost: float = SEA_COST,
) -> tuple[np.ndarray, np.ndarray]:
    """Base land/sea friction plus additive natural barriers.

    ``barriers`` is an iterable of ``(geometry, extra_cost)`` — each feature adds
    its cost per overlapping cell (Tier-0 maps barrier ordinals to these numbers).
    Returns ``(friction, land_mask)``.
    """
    land_mask = rasterize_geom(grid, land_geom)
    friction = np.where(land_mask, 1.0, sea_cost)
    for geom, extra in barriers:
        friction = friction + rasterize_geom(grid, geom) * float(extra)
    return friction, land_mask


def carve_gates(
    friction: np.ndarray,
    gate_rc: Iterable[tuple[int, int]],
    sea_cost: float = SEA_COST,
    radius: int = GATE_RADIUS,
    gate_cost: float = GATE_COST,
) -> np.ndarray:
    """Punch low-cost notches through barriers at held passes.

    A barrier is a wall *with gates*: a held pass (Syrian/Cilician Gates) lowers
    cost in a disc so control flows to the far side. Sea cells are never carved.
    """
    out = friction.copy()
    height, width = out.shape
    for r, c in gate_rc:
        r, c = int(r), int(c)
        r0, r1 = max(0, r - radius), min(height, r + radius + 1)
        c0, c1 = max(0, c - radius), min(width, c + radius + 1)
        yy, xx = np.ogrid[r0:r1, c0:c1]
        disc = (yy - r) ** 2 + (xx - c) ** 2 <= radius ** 2
        block = out[r0:r1, c0:c1]
        land = block < sea_cost
        block[disc & land] = np.minimum(block[disc & land], gate_cost)
        out[r0:r1, c0:c1] = block
    return out


# --- XTENT influence + allocation -------------------------------------------
def influence_field(
    friction: np.ndarray,
    seeds: Iterable[tuple[int, int, float]],
    k: float,
    exponent: float = WEIGHT_EXPONENT,
) -> np.ndarray:
    """Per-entity XTENT influence field ``I = C^a - k·cost``.

    ``seeds`` are ``(row, col, weight)`` triples. Same-weight seeds share one
    cost-distance front (max over weight tiers), so a polity's field is the upper
    envelope of its centers. Cells with no seeds keep ``-inf``.
    """
    influence = np.full(friction.shape, -np.inf)
    tiers: dict[float, list[tuple[int, int]]] = {}
    for r, c, weight in seeds:
        tiers.setdefault(float(weight), []).append((int(r), int(c)))
    for weight, starts in tiers.items():
        costs = MCP_Geometric(friction).find_costs(starts)[0]
        influence = np.maximum(influence, (weight ** exponent) - k * costs)
    return influence


def allocate(
    fields: np.ndarray, rule: str = "B"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Allocate cells to entities. Rule B: argmax among positive influence.

    ``fields`` is an ``(E, H, W)`` stack of influence fields. Returns:

    * ``label`` — ``(H, W)`` int, ``0`` unclaimed else ``entity_index + 1``;
    * ``claimed`` — bool mask where the top field is ``> 0``;
    * ``margin`` — ``(H, W)`` top1−top2 influence (small = contested border).

    The ``I > 0`` cutoff gives each center a natural maximum reach; the border
    falls where two fields cross — inter-polity borders form for free.
    """
    if rule != "B":
        raise ValueError(f"unsupported allocation rule: {rule!r}")
    n_entities = fields.shape[0]
    best = fields.argmax(axis=0)
    top = fields.max(axis=0)
    claimed = top > 0.0
    label = np.zeros(fields.shape[1:], dtype=int)
    for idx in range(n_entities):
        label[claimed & (best == idx)] = idx + 1
    if n_entities >= 2:
        part = np.partition(fields, -2, axis=0)
        margin = part[-1] - part[-2]
    else:
        margin = top
    return label, claimed, margin


def contested_border(
    label: np.ndarray, margin: np.ndarray, threshold: float = CONTEST_MARGIN
) -> np.ndarray:
    """Thin ribbon of border cells where two entities' influence nearly ties.

    A cell qualifies when it sits on a border between two different claimed
    entities *and* the top1−top2 ``margin`` there is below ``threshold``. This is a
    presentation attribute (rendered as a hatch along the boundary), not an
    allocation change — the cell still belongs to its argmax winner.
    """
    border = np.zeros(label.shape, dtype=bool)
    # a seam exists between two adjacent cells that are both claimed by different
    # entities; mark both sides. Slice comparisons avoid np.roll edge wraparound.
    vert = (label[:-1, :] > 0) & (label[1:, :] > 0) & (label[:-1, :] != label[1:, :])
    border[:-1, :] |= vert
    border[1:, :] |= vert
    horiz = (label[:, :-1] > 0) & (label[:, 1:] > 0) & (label[:, :-1] != label[:, 1:])
    border[:, :-1] |= horiz
    border[:, 1:] |= horiz
    return border & (margin < threshold)


# --- route corridors (tapered wedge) ----------------------------------------
def least_cost_path(
    friction: np.ndarray, ordered_rc: Sequence[tuple[int, int]]
) -> list[tuple[int, int]]:
    """Least-cost path through an ordered node chain over ``friction``."""
    pts = [(int(r), int(c)) for r, c in ordered_rc]
    path: list[tuple[int, int]] = []
    for a, b in zip(pts, pts[1:]):
        mcp = MCP_Geometric(friction)
        mcp.find_costs([a])
        seg = [tuple(p) for p in mcp.traceback(b)]
        if path and seg and path[-1] == seg[0]:
            seg = seg[1:]
        path.extend(seg)
    return path


def taper_mask(
    shape: tuple[int, int],
    path: Sequence[tuple[int, int]],
    w_start: float = CORRIDOR_W_START,
    w_end: float = CORRIDOR_W_END,
) -> np.ndarray:
    """Variable-radius buffer along a path: a cone wide at index 0, narrowing to
    a point at the end. Widths are half-widths in grid cells."""
    height, width = shape
    mask = np.zeros((height, width), dtype=bool)
    n = max(len(path) - 1, 1)
    for i, (r, c) in enumerate(path):
        rad = w_start * (1 - i / n) + w_end * (i / n)
        rr = int(np.ceil(rad))
        if rr <= 0:
            mask[r, c] = True
            continue
        r0, r1 = max(0, r - rr), min(height, r + rr + 1)
        c0, c1 = max(0, c - rr), min(width, c + rr + 1)
        yy, xx = np.ogrid[r0:r1, c0:c1]
        mask[r0:r1, c0:c1] |= (yy - r) ** 2 + (xx - c) ** 2 <= rad * rad
    return mask


def corridor_mask(
    friction: np.ndarray,
    ordered_rc: Sequence[tuple[int, int]],
    w_start: float = CORRIDOR_W_START,
    w_end: float = CORRIDOR_W_END,
) -> np.ndarray:
    """Tapered route corridor: least-cost path between ordered nodes + taper.

    Linear control (a road/castle chain through uncontrolled land) that point-seed
    XTENT cannot represent. Fewer than two in-grid nodes → an empty mask.
    """
    pts = [(int(r), int(c)) for r, c in ordered_rc]
    if len(pts) < 2:
        return np.zeros(friction.shape, dtype=bool)
    path = least_cost_path(friction, pts)
    return taper_mask(friction.shape, path, w_start, w_end)


# --- presentation cleanup ---------------------------------------------------
def cleanup(
    label: np.ndarray, land_mask: np.ndarray, max_fill: int = CLEANUP_FILL_CELLS
) -> np.ndarray:
    """Fill small unclaimed gaps by nearest claimed entity, distance-limited.

    Sized to bridge a mountain ridge (~18 km): both sides fill inward and meet on
    the medial line, so a high-cost range renders as a centerline border, not a
    gap. The deep-desert vacuum (far wider than 2× the limit) keeps its unclaimed
    core. Then close fully-enclosed holes. A display-policy knob; never mutates
    allocation.
    """
    from scipy.ndimage import binary_fill_holes, distance_transform_edt

    out = label.copy()
    claimed = out > 0
    if claimed.any():
        dist, (ir, ic) = distance_transform_edt(~claimed, return_indices=True)
        nearest = out[ir, ic]
        fill = (~claimed) & land_mask & (dist <= max_fill)
        out[fill] = nearest[fill]
    for idx in range(1, int(out.max()) + 1):
        holes = binary_fill_holes(out == idx) & (out == 0) & land_mask
        out[holes] = idx
    return out


def fill_coastal_gaps(
    label: np.ndarray,
    land_mask: np.ndarray,
    max_cells: int = 96,
    min_neighbor_share: float = 0.75,
    min_neighbor_cells: int = 2,
    return_diagnostics: bool = False,
) -> np.ndarray | tuple[np.ndarray, list[dict[str, Any]]]:
    """Assign tiny unclaimed coastal land pockets to their dominant neighbour.

    This is for coastline-source mismatches and narrow peninsula tips after the
    honest XTENT allocation. A component is eligible only when it is unclaimed
    land, touches sea on the supplied final land mask, does not touch the raster
    bbox edge, is small, and has one neighbouring polity dominate claimed contact.
    """
    from scipy.ndimage import binary_dilation
    from scipy.ndimage import label as cc_label

    out = label.copy()
    diagnostics: list[dict[str, Any]] = []
    candidates = (out == 0) & land_mask
    if not candidates.any():
        return (out, diagnostics) if return_diagnostics else out

    def record(
        component_id: int,
        reason: str,
        comp: np.ndarray,
        *,
        assigned_label: int = 0,
        best_label: int = 0,
        best_neighbor_cells: int = 0,
        total_neighbor_cells: int = 0,
        touches_sea: bool = False,
        touches_bbox_edge: bool = False,
    ) -> None:
        if not return_diagnostics:
            return
        rr, cc = np.where(comp)
        share = (
            float(best_neighbor_cells) / float(total_neighbor_cells)
            if total_neighbor_cells
            else 0.0
        )
        diagnostics.append(
            {
                "component_id": int(component_id),
                "reason": reason,
                "cells": int(comp.sum()),
                "assigned_label": int(assigned_label),
                "best_label": int(best_label),
                "best_neighbor_cells": int(best_neighbor_cells),
                "total_neighbor_cells": int(total_neighbor_cells),
                "neighbor_share": share,
                "touches_sea": bool(touches_sea),
                "touches_bbox_edge": bool(touches_bbox_edge),
                "row": float(rr.mean()) if rr.size else np.nan,
                "col": float(cc.mean()) if cc.size else np.nan,
            }
        )

    structure = np.ones((3, 3), dtype=bool)
    comps, n = cc_label(candidates, structure=structure)
    for k in range(1, n + 1):
        comp = comps == k
        cells = int(comp.sum())
        if cells == 0:
            continue
        if cells > max_cells:
            record(k, "too_large", comp)
            continue
        touches_bbox_edge = bool(
            comp[0, :].any() or comp[-1, :].any() or comp[:, 0].any() or comp[:, -1].any()
        )
        if touches_bbox_edge:
            record(k, "touches_bbox_edge", comp, touches_bbox_edge=True)
            continue
        border = binary_dilation(comp, structure=structure) & ~comp
        touches_sea = bool((border & ~land_mask).any())
        if not touches_sea:
            record(k, "not_coastal", comp, touches_sea=False)
            continue
        neigh = out[border]
        neigh = neigh[neigh > 0]
        if neigh.size < min_neighbor_cells:
            record(k, "insufficient_neighbor_contact", comp, touches_sea=True)
            continue
        counts = np.bincount(neigh)
        best = int(counts[1:].argmax() + 1)
        total = int(counts[1:].sum())
        if total <= 0 or counts[best] < min_neighbor_cells:
            record(k, "insufficient_neighbor_contact", comp, touches_sea=True)
            continue
        share = float(counts[best]) / float(total)
        if share < min_neighbor_share:
            record(
                k,
                "neighbor_share_below_threshold",
                comp,
                best_label=best,
                best_neighbor_cells=int(counts[best]),
                total_neighbor_cells=total,
                touches_sea=True,
            )
            continue
        out[comp] = best
        record(
            k,
            "accepted",
            comp,
            assigned_label=best,
            best_label=best,
            best_neighbor_cells=int(counts[best]),
            total_neighbor_cells=total,
            touches_sea=True,
        )
    return (out, diagnostics) if return_diagnostics else out


def smooth_labels(label: np.ndarray, min_agree: int = 5, iterations: int = 1) -> np.ndarray:
    """Conservative joint despeckle of a label raster (presentation only).

    A cell flips to a neighbour label only when at least ``min_agree`` of its 8
    neighbours already carry that single label — rounding the staircase jags of a
    raster border. Because every entity reads the same neighbour counts, shared
    borders smooth identically (no slivers, unlike per-polygon vector simplify), and
    solid bodies are untouched while only protruding cells move. Cells never become
    unclaimed. This is a cartographic step; it must not be fed back into allocation.
    """
    from scipy.ndimage import convolve

    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    out = label.copy()
    for _ in range(max(1, iterations)):
        best_count = np.zeros(out.shape, dtype=int)
        best_label = out.copy()
        for value in np.unique(out):
            if value == 0:
                continue
            count = convolve((out == value).astype(int), kernel, mode="constant", cval=0)
            take = count > best_count
            best_count = np.where(take, count, best_count)
            best_label = np.where(take, value, best_label)
        flip = (best_count >= min_agree) & (best_label != out)
        out = np.where(flip, best_label, out)
    return out


def remove_orphans(
    label: np.ndarray,
    n_entities: int,
    seed_rc: dict[int, Sequence[tuple[int, int]]],
    max_orphan_cells: int = MAX_ORPHAN_CELLS,
) -> np.ndarray:
    """Reassign seedless enclosed islands to the surrounding entity.

    A low-decay ("expansive") rival's field can poke through a local minimum and
    leave an island of itself with no seed inside another entity. Such small
    seedless components are artifacts; genuine exclaves (which carry a seed) and
    large components are preserved. ``seed_rc`` maps entity index → its seed cells.
    """
    from scipy.ndimage import binary_dilation
    from scipy.ndimage import label as cc_label

    out = label.copy()
    for idx in range(n_entities):
        comps, n = cc_label(out == idx + 1)
        for k in range(1, n + 1):
            comp = comps == k
            if int(comp.sum()) > max_orphan_cells:
                continue
            if any(comp[r, c] for r, c in seed_rc.get(idx, [])):
                continue  # legitimate exclave (has its own seed)
            border = binary_dilation(comp) & ~comp
            neigh = out[border]
            neigh = neigh[(neigh > 0) & (neigh != idx + 1)]
            out[comp] = np.bincount(neigh).argmax() if neigh.size else 0
    return out


# --- vectorization ----------------------------------------------------------
def vectorize(label: np.ndarray, transform: Any, entities: Sequence[str], crs: str = "EPSG:4326"):
    """Polygonize the label raster into a per-entity GeoDataFrame.

    ``rasterio.features.shapes`` per entity → dissolve to one (multi)polygon.
    Returns ``GeoDataFrame[entity, geometry]``; entities with no cells are dropped.
    """
    import geopandas as gpd
    from shapely import union_all
    from shapely.geometry import shape as to_shape

    records = []
    for idx, entity in enumerate(entities):
        mask = label == idx + 1
        if not mask.any():
            continue
        geoms = [
            to_shape(geom)
            for geom, val in rasterio.features.shapes(
                mask.astype("uint8"), mask=mask, transform=transform
            )
            if val == 1
        ]
        if not geoms:
            continue
        records.append({"entity": entity, "geometry": union_all(geoms)})
    return gpd.GeoDataFrame(records, geometry="geometry", crs=crs)
