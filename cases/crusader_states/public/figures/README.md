# Figure captions and interpretation

Regenerate every figure and metric from the repository root:

```bash
PYTHONPATH=src python3 -m historical_geo figures cases/crusader_states/public
```

## `evidence-anchors.png`

Named locality anchors recovered from historical claims. GeoNames coordinates are approximate. Mountain polygons and the Jordan River provide modern geographic context; they do not independently prove political control.

## `reconstruction-slices.png`

Reviewed-baseline allocations for 1130 and end-of-year 1187. Colored polygons are XTENT boundary hypotheses generated from reviewed point seeds and declared model ordinals. They are not observed borders. Small retained seed cells may be hard to see at this scale.

## `natural-ablation.png`

The left column removes mountain costs; the right applies the bounded `soft` Mount Lebanon and `porous` Taurus assumptions. Natural Earth supplies feature geometry, while the friction ordinals remain modeling choices. `natural-ablation.json` reports symmetric-difference area as model sensitivity, not accuracy.

## `boundary-attractor-diagnostics.png`

A synthetic near-parallel candidate is accepted only after topology and area guards pass. The real Jordan River candidate is rejected for direction mismatch, and the source geometry is never mutated. The river is context, not evidence that the historical shared edge followed it.

## `reference-comparison.png`

Project-authored counts of categorical assertions from the registered external maps: named city control, retained entities, and expressed adjacency. A rights-blocked 1130 map remains in the register but contributes no extracted assertion. `reference-comparison.json` stores the item-level result. No atlas scan, traced boundary, IoU, or historical accuracy score appears here.

## `uncertainty-zones.png`

Agreement classes across the declared evidence and model scenarios on a common 10 km analysis grid. Stable core, evidence-sensitive, model-sensitive, and unresolved indicate behavior within this scenario set. They are not probabilities or confidence intervals. Exact area and agreement summaries are in `uncertainty-zones.json`.

`figure-qa.json` records dimensions, nonblank checks, and SHA-256 values for all six PNG files after regeneration.
