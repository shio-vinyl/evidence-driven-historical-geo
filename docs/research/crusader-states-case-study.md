[English](crusader-states-case-study.md) | [简体中文](crusader-states-case-study.zh-CN.md)

# Crusader States Case Study

## Scope

This case tests an agent-led evidence-to-XTENT workflow on two bounded slices: **1130** and **end of 1187**. The agent gathered and checked sources, separated point control from political centers and campaign events, resolved seven load-bearing gaps, and built scenarios around the decisions it could not close.

The fixture contains citations, short project paraphrases, approximate GeoNames points, clipped public-domain physical vectors, and machine-readable review records. It contains no source PDF, atlas page, or traced copyrighted geometry.

## Slice definitions

The 1130 slice captures a multi-polity landscape. Its reviewed baseline now contains Jerusalem, Burid Damascus, Tripoli, Antioch, and Edessa. Fatimid Egypt is absent because its only public-case seed, Ascalon, remains disputed. The inclusive scenario restores Ascalon and Tortosa for sensitivity testing.

The end-1187 slice uses an explicit year-end convention. Its baseline contains an Ayyubid surface and Latin centers at Tyre, Tripoli, and Antioch. Cairo and Jaffa are omitted from the baseline and activated only in the inclusive scenario.

## Evidence decisions

The seven formerly partial or unresolved groups no longer share one ambiguous status.

| Group | Decision | Baseline consequence |
|---|---|---|
| Jaffa in the 1187 coast group | DISPUTED | Omitted; inclusive only. |
| Ascalon in 1130 | DISPUTED | Fatimid Egypt omitted; inclusive only. |
| Cairo/Damascus in 1187 | DOWNGRADE | Damascus retained; Cairo inclusive only. |
| Antioch in 1187 | KEEP | City point retained; no surrounding lordships inferred. |
| Edessa from adjacent 1131 material | DOWNGRADE | Retained at minor seed weight. |
| Tripoli/Tortosa in 1130 | DOWNGRADE | Tripoli retained; Tortosa inclusive only. |
| Tripoli at end of 1187 | KEEP | City point retained; inland county extent unresolved. |

The machine-readable table is `historical-claim-decisions.json`. Lineage records carry the same decisions, so excluded baseline inputs cannot return through adapter defaults.

## Reconstruction

![1130 and end-of-1187 boundary hypotheses](../../cases/crusader_states/public/figures/reconstruction-slices.png)

The reviewed-baseline runs retain five entities in 1130 and four in 1187. Every surface is valid and non-overlapping. Point ownership keeps a reviewed locality visible in its raster cell; it does not grant a larger territory.

The generated edges remain grid-derived boundary hypotheses. Missing areas in 1130, especially the absent Fatimid surface, record the evidence decision rather than a claim that no Fatimid polity existed.

## External comparison

![Categorical external comparison](../../cases/crusader_states/public/figures/reference-comparison.png)

The public-domain Shepherd c.1140 plate agrees with 12 of 17 recorded city, entity, and adjacency assertions. Its main reference-only items are Ascalon, Tortosa, Fatimid Egypt, and two adjacencies affected by the missing Fatimid surface or model geometry.

For 1187, Shepherd c.1190 agrees on all four expressed entities. Johnston’s 1187–1190 campaign map agrees on 13 of 14 recorded city/entity assertions; Jaffa is the single reference-only city. Buck’s exact 1130 map is registered but not extracted because the legal preview does not expose the copyrighted map page.

## Scenario analysis

![Scenario agreement zones](../../cases/crusader_states/public/figures/uncertainty-zones.png)

Eight scenarios cover verified-only evidence, the reviewed baseline, disputed inclusions, flat natural cost, two wider projection ordinals, and 5/10/20 km grids. At 1130, 13.65% of assessed cells form stable core and 81.59% are model-sensitive. At 1187, stable core is 12.98%, model-sensitive area 75.44%, evidence-sensitive area 2.36%, and unresolved area 9.22%.

The strong projection response is part of the result. It shows that the current sparse point set supports stable local cores more readily than stable regional extent.

## Natural cost and boundary attractor

Mount Lebanon and Taurus remain assumption-labeled costs. `flat-natural` removes both. Their symmetric difference is a model diagnostic.

The Jordan River remains display context and a rejected real attractor candidate. Its direction similarity is `0.0209` against a required `0.8`, so the source geometry is unchanged. A nearby modern line does not become historical boundary evidence through proximity.

## Verification

The case passes public lineage validation, all required scenario rebuilds, entity-retention checks, geometry validity, non-overlap checks, six-figure QA, and fixture hash verification. Full commands and generated outputs are listed in the [Reproducibility Guide](../operations/reproducibility.md).

## Historical review still required

Code cannot decide whether adjacent-year Edessa evidence is acceptable, whether the “sultan of Egypt” wording permits a Cairo point, whether Jaffa should follow the campaign map despite the primary-page gap, or how much temporal weight a c.1140 or c.1190 comparator deserves. The project remains a research prototype until a historian accepts or revises those judgments.
