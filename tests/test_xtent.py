"""Synthetic unit tests recovered for the cost-distance XTENT core."""

from __future__ import annotations

import unittest
import numpy as np
from pyproj import Transformer
from rasterio.transform import rowcol
from shapely.geometry import box

from historical_geo import xtent



class OrdinalMappingTest(unittest.TestCase):
    def test_projection_k_is_bounded_and_monotone(self) -> None:
        # expansive polities project farther → smaller decay than contracted ones
        self.assertLess(xtent.projection_k("expansive"), xtent.projection_k("normal"))
        self.assertLess(xtent.projection_k("normal"), xtent.projection_k("contracted"))

    def test_seed_weight_known_and_default(self) -> None:
        self.assertEqual(xtent.seed_weight("capital"), 4.0)
        self.assertEqual(xtent.seed_weight("castle"), 1.6)
        self.assertEqual(xtent.seed_weight("unknown_type"), xtent.WEIGHT_DEFAULT)
        self.assertEqual(xtent.seed_weight(None), xtent.WEIGHT_DEFAULT)

    def test_weight_ordinal_ranks_monotone(self) -> None:
        ranks = [xtent.weight_ordinal(r) for r in ("outpost", "minor", "major", "capital")]
        self.assertEqual(ranks, sorted(ranks))

    def test_barrier_cost_ordinals_monotone(self) -> None:
        self.assertLess(xtent.barrier_cost("porous"), xtent.barrier_cost("soft"))
        self.assertLess(xtent.barrier_cost("soft"), xtent.barrier_cost("hard"))

    def test_sea_cost_profiles(self) -> None:
        # a maritime power treats the sea as a highway, not a wall
        self.assertLess(
            xtent.sea_cost_for_profile("maritime"), xtent.sea_cost_for_profile("settled")
        )

    def test_corridor_width_returns_body_and_tip(self) -> None:
        body, tip = xtent.corridor_width("narrow")
        self.assertGreater(body, tip)
        self.assertEqual(tip, 0.0)
        self.assertGreater(xtent.corridor_width("normal")[0], body)


class GridTest(unittest.TestCase):
    def test_build_grid_shape_and_transform(self) -> None:
        grid = xtent.build_grid((0.0, 0.0, 4.0, 2.0), res=0.5)
        self.assertEqual((grid.height, grid.width), (4, 8))
        self.assertEqual(grid.shape, (4, 8))
        # cell 0 maps to the NW corner (origin upper)
        self.assertAlmostEqual(grid.transform.c, 0.0)
        self.assertAlmostEqual(grid.transform.f, 2.0)

    def test_rasterize_geom_burns_box(self) -> None:
        grid = xtent.build_grid((0.0, 0.0, 4.0, 4.0), res=1.0)
        mask = xtent.rasterize_geom(grid, box(1.0, 1.0, 3.0, 3.0))
        self.assertEqual(mask.dtype, np.bool_)
        self.assertEqual(int(mask.sum()), 4)

    def test_rasterize_geom_handles_none(self) -> None:
        grid = xtent.build_grid((0.0, 0.0, 2.0, 2.0), res=1.0)
        self.assertFalse(xtent.rasterize_geom(grid, None).any())

    def test_build_grid_projected_equal_area(self) -> None:
        # a metric equal-area CRS: res is in metres, bbox stays lon/lat for reference
        grid = xtent.build_grid(
            (33.8, 28.8, 38.6, 37.7), 2000,
            "+proj=laea +lat_0=33 +lon_0=36 +datum=WGS84 +units=m",
        )
        self.assertGreater(grid.width, 100)
        self.assertGreater(grid.height, 100)
        self.assertEqual(grid.bbox, (33.8, 28.8, 38.6, 37.7))
        self.assertFalse(str(grid.crs).startswith("EPSG:4326"))

    def test_build_grid_projected_bbox_samples_curved_edges(self) -> None:
        crs = "+proj=laea +lat_0=47 +lon_0=100 +datum=WGS84 +units=m"
        grid = xtent.build_grid((70.0, 34.0, 126.0, 58.0), 10000, crs)
        tf = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        x, y = tf.transform(114.3076, 34.7973)  # Kaifeng, inside lon/lat bbox.
        row, col = rowcol(grid.transform, x, y)
        self.assertGreaterEqual(row, 0)
        self.assertLess(row, grid.height)
        self.assertGreaterEqual(col, 0)
        self.assertLess(col, grid.width)


class CoastalGapFillTest(unittest.TestCase):
    def test_fill_coastal_gap_assigns_small_tip_to_dominant_neighbor(self) -> None:
        label = np.zeros((7, 7), dtype=int)
        land = np.zeros((7, 7), dtype=bool)
        land[1:6, 1:6] = True
        land[3, 5] = False  # sea notch beside the unclaimed coastal tip
        label[land] = 1
        label[3, 4] = 0

        out = xtent.fill_coastal_gaps(label, land, max_cells=4, min_neighbor_share=0.75)

        self.assertEqual(int(out[3, 4]), 1)

    def test_fill_coastal_gap_rejects_bbox_edge_components(self) -> None:
        label = np.zeros((5, 5), dtype=int)
        land = np.ones((5, 5), dtype=bool)
        land[1, 1] = False
        label[1:4, 1:3] = 1
        label[0, 2] = 0

        out = xtent.fill_coastal_gaps(label, land, max_cells=4, min_neighbor_share=0.75)

        self.assertEqual(int(out[0, 2]), 0)

    def test_fill_coastal_gap_returns_diagnostics_when_requested(self) -> None:
        label = np.zeros((7, 7), dtype=int)
        land = np.zeros((7, 7), dtype=bool)
        land[1:6, 1:6] = True
        land[3, 5] = False
        label[land] = 1
        label[3, 4] = 0

        out, diagnostics = xtent.fill_coastal_gaps(
            label,
            land,
            max_cells=4,
            min_neighbor_share=0.75,
            return_diagnostics=True,
        )

        self.assertEqual(int(out[3, 4]), 1)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0]["reason"], "accepted")
        self.assertEqual(diagnostics[0]["assigned_label"], 1)


class FrictionTest(unittest.TestCase):
    def test_build_friction_land_sea_and_barriers(self) -> None:
        grid = xtent.build_grid((0.0, 0.0, 4.0, 4.0), res=1.0)
        land = box(0.0, 0.0, 4.0, 4.0)
        barrier = box(1.0, 1.0, 2.0, 2.0)
        friction, land_mask = xtent.build_friction(grid, land, [(barrier, 9.0)], sea_cost=30.0)
        self.assertTrue(land_mask.all())
        # land base cost is 1.0; the barrier cell carries 1.0 + 9.0
        self.assertEqual(float(friction.min()), 1.0)
        self.assertEqual(float(friction.max()), 10.0)

    def test_build_friction_marks_sea(self) -> None:
        grid = xtent.build_grid((0.0, 0.0, 4.0, 4.0), res=1.0)
        friction, land_mask = xtent.build_friction(grid, box(0.0, 0.0, 2.0, 4.0), sea_cost=30.0)
        # left half is land (1.0), right half is sea (30.0)
        self.assertTrue((friction[:, :2] == 1.0).all())
        self.assertTrue((friction[:, 2:] == 30.0).all())
        self.assertEqual(int(land_mask.sum()), 8)

    def test_carve_gates_lowers_only_land(self) -> None:
        friction = np.full((11, 11), 20.0)
        friction[:, 5] = 1.0  # a thin land corridor; the rest is "sea" at 20
        carved = xtent.carve_gates(
            friction, [(5, 5)], sea_cost=20.0, radius=3, gate_cost=1.5
        )
        # the gate cell is carved; surrounding sea (>= sea_cost) is untouched
        self.assertEqual(carved[5, 5], 1.0)
        self.assertEqual(carved[5, 0], 20.0)
        self.assertTrue((carved <= friction + 1e-9).all())


class InfluenceAllocateTest(unittest.TestCase):
    def test_influence_decays_with_cost(self) -> None:
        friction = np.ones((1, 10))
        field = xtent.influence_field(friction, [(0, 0, 4.0)], k=0.5)
        # closest cell scores highest; influence falls off with distance
        self.assertEqual(field.argmax(), 0)
        self.assertGreater(field[0, 0], field[0, 5])
        self.assertTrue(np.all(np.diff(field[0]) <= 1e-9))

    def test_influence_max_over_weight_tiers(self) -> None:
        friction = np.ones((1, 11))
        # a small seed at the left, a big one at the right; field is the envelope
        field = xtent.influence_field(friction, [(0, 0, 2.0), (0, 10, 4.0)], k=0.1)
        self.assertGreaterEqual(field[0, 10], field[0, 0])
        self.assertEqual(field.argmax(), 10)

    def test_allocate_rule_b_argmax_and_threshold(self) -> None:
        # two entities, one each side; a far cell scores <=0 for both → unclaimed
        friction = np.ones((1, 21))
        a = xtent.influence_field(friction, [(0, 0, 3.0)], k=0.5)
        b = xtent.influence_field(friction, [(0, 20, 3.0)], k=0.5)
        label, claimed, margin = xtent.allocate(np.stack([a, b]))
        self.assertEqual(label[0, 0], 1)
        self.assertEqual(label[0, 20], 2)
        self.assertEqual(label[0, 10], 0)  # midpoint beyond reach of both
        self.assertFalse(claimed[0, 10])
        self.assertTrue((margin >= 0).all())

    def test_allocate_rejects_unknown_rule(self) -> None:
        with self.assertRaises(ValueError):
            xtent.allocate(np.zeros((2, 2, 2)), rule="A")


class ContestedBorderTest(unittest.TestCase):
    def test_marks_near_tie_boundary(self) -> None:
        label = np.array([[1, 1, 2, 2]])
        margin = np.full((1, 4), 0.1)
        out = xtent.contested_border(label, margin, threshold=0.3)
        self.assertTrue(out[0, 1] and out[0, 2])  # the two cells across the 1|2 seam
        self.assertFalse(out[0, 0] or out[0, 3])  # interiors are not contested

    def test_confident_border_is_not_contested(self) -> None:
        label = np.array([[1, 1, 2, 2]])
        out = xtent.contested_border(label, np.full((1, 4), 1.0), threshold=0.3)
        self.assertFalse(out.any())

    def test_edge_with_unclaimed_is_not_contested(self) -> None:
        # a border against no-man's-land (0) is a frontier, not a contested tie
        label = np.array([[1, 1, 0, 0]])
        out = xtent.contested_border(label, np.full((1, 4), 0.1), threshold=0.3)
        self.assertFalse(out.any())


class CorridorTest(unittest.TestCase):
    def test_least_cost_path_follows_low_friction(self) -> None:
        friction = np.full((5, 5), 10.0)
        friction[2, :] = 1.0  # cheap middle row
        path = xtent.least_cost_path(friction, [(2, 0), (2, 4)])
        self.assertEqual(path[0], (2, 0))
        self.assertEqual(path[-1], (2, 4))
        self.assertTrue(all(r == 2 for r, _ in path))

    def test_taper_mask_narrows_to_tip(self) -> None:
        path = [(10, c) for c in range(0, 20)]
        mask = xtent.taper_mask((21, 21), path, w_start=4.0, w_end=0.0)
        width_at_start = int(mask[:, path[0][1]].sum())
        width_at_end = int(mask[:, path[-1][1]].sum())
        self.assertGreater(width_at_start, width_at_end)
        self.assertGreaterEqual(width_at_end, 1)

    def test_corridor_mask_needs_two_nodes(self) -> None:
        friction = np.ones((5, 5))
        self.assertFalse(xtent.corridor_mask(friction, [(2, 2)]).any())
        self.assertTrue(xtent.corridor_mask(friction, [(2, 0), (2, 4)]).any())


class CleanupTest(unittest.TestCase):
    def test_cleanup_bridges_ridge_to_medial_line(self) -> None:
        # two claims separated by a one-cell unclaimed strip → fills to a border
        label = np.zeros((1, 7), dtype=int)
        label[0, :3] = 1
        label[0, 4:] = 2
        land = np.ones((1, 7), dtype=bool)
        out = xtent.cleanup(label, land, max_fill=8)
        self.assertEqual(out[0, 3], 1)  # nearest claimed (tie → lower index by edt)
        self.assertFalse((out == 0).any())

    def test_cleanup_preserves_wide_vacuum(self) -> None:
        # a gap wider than 2× max_fill keeps an unclaimed core
        label = np.zeros((1, 41), dtype=int)
        label[0, :5] = 1
        label[0, 36:] = 2
        land = np.ones((1, 41), dtype=bool)
        out = xtent.cleanup(label, land, max_fill=3)
        self.assertTrue((out[0, 10:30] == 0).all())

    def test_cleanup_does_not_fill_sea(self) -> None:
        label = np.zeros((1, 5), dtype=int)
        label[0, 0] = 1
        land = np.array([[True, True, False, False, False]])
        out = xtent.cleanup(label, land, max_fill=8)
        self.assertTrue((out[0, 2:] == 0).all())


class OrphanTest(unittest.TestCase):
    def test_remove_orphans_reassigns_seedless_island(self) -> None:
        label = np.full((5, 5), 1, dtype=int)
        label[2, 2] = 2  # a single seedless cell of entity 2 inside entity 1
        out = xtent.remove_orphans(label, n_entities=2, seed_rc={0: [(0, 0)], 1: []})
        self.assertEqual(out[2, 2], 1)

    def test_remove_orphans_keeps_seeded_exclave(self) -> None:
        label = np.full((5, 5), 1, dtype=int)
        label[2, 2] = 2
        out = xtent.remove_orphans(label, n_entities=2, seed_rc={0: [(0, 0)], 1: [(2, 2)]})
        self.assertEqual(out[2, 2], 2)  # genuine exclave preserved

    def test_remove_orphans_keeps_large_component(self) -> None:
        label = np.full((10, 10), 1, dtype=int)
        label[:5, :5] = 2  # a big seedless block but above the size cap
        out = xtent.remove_orphans(
            label, n_entities=2, seed_rc={0: [], 1: []}, max_orphan_cells=5
        )
        self.assertTrue((out[:5, :5] == 2).all())


class SmoothLabelsTest(unittest.TestCase):
    def test_removes_single_cell_speck(self) -> None:
        label = np.ones((5, 5), dtype=int)
        label[2, 2] = 2  # a lone speck surrounded by entity 1
        out = xtent.smooth_labels(label, min_agree=5)
        self.assertEqual(out[2, 2], 1)

    def test_straight_border_is_untouched(self) -> None:
        label = np.zeros((6, 6), dtype=int)
        label[:, :3] = 1
        label[:, 3:] = 2
        out = xtent.smooth_labels(label, min_agree=5)
        np.testing.assert_array_equal(out, label)  # no cell has ≥5 cross-neighbours

    def test_never_unclaims_a_cell(self) -> None:
        label = np.zeros((5, 5), dtype=int)
        label[2, 2] = 1
        out = xtent.smooth_labels(label, min_agree=5)
        self.assertEqual(out[2, 2], 1)  # 0 is never a flip target


class VectorizeTest(unittest.TestCase):
    def test_vectorize_emits_per_entity_polygons(self) -> None:
        grid = xtent.build_grid((0.0, 0.0, 4.0, 4.0), res=1.0)
        label = np.zeros((4, 4), dtype=int)
        label[:, :2] = 1
        label[:, 2:] = 2
        gdf = xtent.vectorize(label, grid.transform, ["West", "East"], crs=grid.crs)
        self.assertEqual(sorted(gdf["entity"]), ["East", "West"])
        self.assertTrue(gdf.geometry.is_valid.all())
        # each polity covers half the 4×4° land → ~8 deg² each
        self.assertAlmostEqual(sum(geom.area for geom in gdf.geometry), 16.0, places=6)

    def test_vectorize_drops_empty_entities(self) -> None:
        grid = xtent.build_grid((0.0, 0.0, 2.0, 2.0), res=1.0)
        label = np.ones((2, 2), dtype=int)
        gdf = xtent.vectorize(label, grid.transform, ["Only", "Empty"], crs=grid.crs)
        self.assertEqual(list(gdf["entity"]), ["Only"])

