[English](comparative-evaluation.md) | [简体中文](comparative-evaluation.zh-CN.md)

# Comparative Evaluation

## Purpose

This comparison asks a narrow question: where does the reviewed-baseline reconstruction agree with, omit, or differ from published hand-made maps? The maps are external interpretations. None is ground truth, and the counts below are not historical accuracy scores.

The public repository contains no atlas scan and no traced atlas boundary. `reference-map-register.json` stores catalog details, rights, prior use, temporal fit, and hand-recorded categorical observations. `reference-comparison.png` is an original summary chart.

## Reference register

Four items were reviewed.

- Andrew D. Buck, *The Principality of Antioch and its Frontiers in the Twelfth Century* (Boydell Press, 2017), Map 2, “Northern Syria and Cilicia, 1130,” p. 23. This is the only exact-year scholarly map found for part of the 1130 slice. The legal publisher preview confirms the title and page but does not expose the map body, so no assertions or geometry were extracted.
- William R. Shepherd, *Historical Atlas* (1926 ed.), “Asia Minor and the States of the Crusaders in Syria, about 1140,” p. 68. It is public domain and covers the full regional pattern, but it is ten years later than the target.
- Shepherd, *Historical Atlas* (1911), “Europe and the Mediterranean Lands about 1190,” pp. 70–71. It is public domain and useful for entity survival at regional scale. It is too coarse and too late for city or boundary evaluation of end-1187.
- W. & A. K. Johnston / Reginald Lane Poole, “Syria Showing Saladin’s Conquests 1187–1190,” in *Historical Atlas of Modern Europe* (1902). This public-domain campaign map separates 1187, 1188, later fortress captures, and the 1192 Christian boundary.

## Independence and rights

The Shepherd and Johnston plates come from different cartographic lineages. Both were listed in a read-only audit before this public project was assembled, so the comparison is non-blind. That audit produced no seed, polygon, model parameter, or evidence claim. They are external comparators without parameter circularity.

Buck’s exact 1130 map is partly independent of the current evidence set, although Buck also appears as a textual source. Its copyrighted map body was not available through the legal preview. The register records this rights and access block instead of reconstructing the page from unauthorized copies.

## Harmonization before comparison

Dates were kept literal. The 1130 model is compared with c.1140 only as a temporal proxy. End-1187 is compared with c.1190 and an 1187–1190 campaign sequence; later Third Crusade states were not pulled backward into the target slice.

Entity names were aligned only where the equivalence was straightforward, such as “Empire of Saladin” to “Ayyubid Sultanate.” City control, entity presence, adjacency, and coastal place order were recorded separately. Generalized fills, desert edges, and campaign coloring were not converted into boundary lines.

## Categorical results

### 1130

The Shepherd plate expresses 17 comparable city, entity, and adjacency assertions. Twelve agree with the reviewed baseline. The five reference-only items are Fatimid Egypt as a retained entity, Ascalon and Tortosa as city points, and two adjacencies involving the omitted Fatimid surface or the Jerusalem–Tripoli contact.

The result locates the disagreement cleanly. Jerusalem, Damascus, Tripoli, Antioch, and Edessa form the shared core. Ascalon and Tortosa enter the inclusive scenario, where their effect can be inspected without placing them in the baseline. No line distance or overlap was calculated because the c.1140 fills are temporally mismatched and highly generalized.

### End of 1187

The c.1190 Shepherd plate expresses four comparable entity-presence assertions; all four entities appear in the reviewed baseline. The Johnston campaign map expresses 14 comparable city and entity assertions. Thirteen agree. Jaffa is the single reference-only city: Johnston assigns it to the 1187 conquest sequence, while the textual page review still does not support the Jaffa member of the grouped coast claim.

This is evidence tension, not a model error score. Jaffa stays out of the baseline and enters the inclusive scenario. Tyre, Tripoli, Antioch, and the broad Ayyubid pattern are the main points of cross-map agreement.

## Interpretation limits

The register records what each map actually expresses and where it is silent. It does not infer an unprinted boundary, treat an old atlas fill as direct observation, or average maps into a consensus border. The comparison was run after the baseline evidence decisions, and no model parameter was changed in response.

## Human review boundary

A historian still needs to judge whether the 1130 proxy comparison is temporally acceptable, whether Johnston’s campaign categories support a point-level Jaffa interpretation, and whether Buck’s exact-year map can be consulted under lawful access. Those decisions can change the scholarly reading, but they cannot be resolved by the current code.
