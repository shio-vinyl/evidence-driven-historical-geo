[English](comparative-evaluation.md) | [简体中文](comparative-evaluation.zh-CN.md)

# Comparative Evaluation

## Scope and evaluation state

The registered hand-made maps are evaluation-only interpretations. None is ground truth, and the categorical counts below are not historical accuracy scores. The repository contains no atlas scan and no traced atlas boundary. [`reference-map-register.json`](../../cases/crusader_states/public/reference-map-register.json) stores catalog, rights, temporal-fit, and hand-recorded categorical observations; [`reference-comparison.png`](../../cases/crusader_states/public/figures/reference-comparison.png) is an original summary.

The checked-in figure and its companion JSON are a **frozen Round-00 evaluation produced through the v0.1 compatibility path**. They describe the reviewed baseline before the first targeted evidence-acquisition round. Round 01 did not consult historical boundary maps while searching for evidence; its [`source-checks.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/source-checks.json) records that guard. No updated held-out comparison count is claimed for Round 01.

## Registered references

Four items were reviewed for the frozen comparison.

- Andrew D. Buck, *The Principality of Antioch and its Frontiers in the Twelfth Century* (Boydell Press, 2017), Map 2, “Northern Syria and Cilicia, 1130,” p. 23. The legal publisher preview confirms the title and page but does not expose the map body, so no assertion or geometry was extracted.
- William R. Shepherd, *Historical Atlas* (1926 ed.), “Asia Minor and the States of the Crusaders in Syria, about 1140,” p. 68. This public-domain plate covers the regional pattern ten years after the target slice.
- Shepherd, *Historical Atlas* (1911), “Europe and the Mediterranean Lands about 1190,” pp. 70–71. This public-domain plate is useful for entity presence at regional scale and too coarse and late for end-1187 boundary evaluation.
- W. & A. K. Johnston / Reginald Lane Poole, “Syria Showing Saladin’s Conquests 1187–1190,” in *Historical Atlas of Modern Europe* (1902). The public-domain campaign map separates the 1187 and 1188 sequences, later fortress captures, and the 1192 Christian boundary.

The Shepherd and Johnston plates come from different cartographic lineages. Both were registered in a read-only audit before assembly of the public project, so the comparison is non-blind. That audit produced no seed, polygon, model parameter, or evidence claim. Buck also appears in the textual bibliography, and the inaccessible map body contributes no extracted assertion.

## Round-00 categorical results

Dates were kept literal. The 1130 reconstruction was compared with c.1140 only as a temporal proxy. End-1187 was compared with c.1190 and the 1187–1190 campaign sequence without pulling later Third Crusade states backward. City control, entity presence, adjacency, and coastal place order were recorded separately; generalized fills and campaign colors were not converted into boundary lines.

For **1130**, Shepherd expresses 17 comparable city, entity, and adjacency assertions. Twelve match the Round-00 reviewed baseline. The five reference-only items are Fatimid Egypt as a retained entity, Ascalon and Tortosa as city points, plus two adjacencies involving the omitted Fatimid surface or the Jerusalem–Tripoli contact. No line distance or overlap was calculated because the proxy is temporally mismatched and highly generalized.

For **end-1187**, the c.1190 Shepherd plate expresses four comparable entity-presence assertions and all four match the Round-00 baseline. The Johnston campaign map expresses 14 comparable city and entity assertions: 13 match, while Jaffa is reference-only. At Round 00, the checked text had not yet supported Jaffa as an admissible point-control input.

## Round-01 status

Round 01 changes how the frozen comparison must be read. Textual checks closed the Jaffa gap and admitted `D_1187_JAFFA_SEED`; its isolated spatial effect remains zero cells. Cairo was also admitted and accounts for the 1,162 changed baseline cells, while Jaffa accounts for none. The old “13 of 14, Jaffa reference-only” line is therefore a historical Round-00 result, not a current performance number.

The 1130 baseline gained Rafaniyya, which is absent from the registered comparison assertions and changes zero grid cells. The Round-00 “12 of 17” count has not been recomputed or promoted as a Round-01 score. The correct current evidence and spatial state is recorded in [`round-delta.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/round-delta.json) and the Round-01 diagnosis files.

## Interpretation boundary

The register records only what each reference explicitly expresses and where it is silent. It does not infer unprinted boundaries, convert old atlas fills into direct observations, or average maps into a consensus border. The frozen comparison did not drive parameter tuning. A historian must still decide whether the 1140 proxy is acceptable for 1130, how to interpret Johnston’s campaign categories, and whether Buck’s exact-year map can be consulted lawfully.
