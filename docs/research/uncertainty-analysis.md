[English](uncertainty-analysis.md) | [简体中文](uncertainty-analysis.zh-CN.md)

# Uncertainty Analysis

## What is measured

The research loop reports deterministic sensitivity inside a declared scenario set. An affected cell changes assignment when one named intervention is compared with the reviewed baseline. The counts are diagnostics of the present evidence and backend; they are neither probabilities nor estimates of historical territorial area.

Two states must be kept separate:

- **Round 00** is the epistemic state before targeted evidence acquisition. Its diagnosis decomposes grouped scenarios into atomic evidence interventions.
- **Round 01** is the state after the Cairo, Edessa, and Tripoli searches, plus the incidental Jaffa cross-check. Its diagnosis reports only unresolved counterfactuals against the updated baseline.

## Round 00: evidence-search priorities

The atomic Round-00 diagnosis measured the following evidence effects on the common 10 km grid:

| Slice | Decision intervention | Affected cells |
|---|---|---:|
| 1130 | add Ascalon | 1 |
| 1130 | restore the Edessa seed | 257 |
| 1130 | add Tortosa | 0 |
| 1130 | restore the Tripoli seed | 220 |
| 1187 | add Cairo | 1,162 |
| 1187 | add Jaffa | 0 |

These marginal effects generated the first search agenda: Cairo, Edessa, and Tripoli ranked above Ascalon; Tortosa and Jaffa were retained in the diagnosis with zero measured marginal effect. Jaffa was nevertheless checked when the Cairo source trail produced directly relevant material.

The stored source of truth is [`rounds/00-initial/uncertainty-diagnosis.json`](../../cases/crusader_states/public/research/rounds/00-initial/uncertainty-diagnosis.json). The older [`uncertainty-zones.png`](../../cases/crusader_states/public/figures/uncertainty-zones.png) and companion JSON are a **frozen Round-00 v0.1 grouped-scenario figure**. Their 1130/1187 percentage summaries remain reproducibility fixtures for that state; they must not be read as Round-01 results or used to rank individual evidence gaps.

## Round 01: updated baseline and residual uncertainty

Round 01 changed the admissibility state before running the same XTENT backend. The baseline-to-baseline delta is recorded in [`round-delta.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/round-delta.json).

- **1130:** admitting Rafaniyya as an additional Tripoli control point changed **0 cells**. The resulting surface was identical to the Round-00 baseline on the declared grid. The remaining evidence interventions are Ascalon (**1 cell**) and Tortosa (**0 cells**). Model variants still dominate: flat natural costs affect 196 cells, normal reach 3,412, and expansive reach 5,736.
- **1187:** admitting Cairo and Jaffa changed **1,162 cells**, all from unassigned to Ayyubid Sultanate. The Round-00 atomic attribution assigns all 1,162 cells to Cairo and zero marginal cells to Jaffa. After both decisions entered the baseline, the Round-01 evidence axis has no remaining variant and therefore affects **0 cells**. The residual diagnosis is model-only: flat natural costs affect 196 cells, normal reach 2,838, and expansive reach 5,182.

The current machine-readable diagnoses are [`uncertainty-diagnosis-1130.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1130.json) and [`uncertainty-diagnosis-1187.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1187.json). No Round-01 categorical uncertainty-zone PNG is claimed; the JSON diagnostics are the current research state.

## Interpretation boundary

Zero marginal effect does not make a claim historically unimportant. It means the current grid, backend, baseline, and intervention order produced no changed assignment. Likewise, the 1,162-cell Cairo expansion records backend response to a newly admitted anchor. It does not validate an Ayyubid boundary or establish historical accuracy. The scenario set remains deliberately bounded, and a historian must still judge source admissibility and the plausibility of the modeled reach classes.
