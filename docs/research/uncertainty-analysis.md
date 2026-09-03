[English](uncertainty-analysis.md) | [简体中文](uncertainty-analysis.zh-CN.md)

# Uncertainty Analysis

## Question

The uncertainty figure measures agreement inside a declared scenario set. It shows which cells keep the same assignment when evidence eligibility or model choices change. It is not a probability map and does not estimate the chance that an entity historically controlled a cell.

## Scenario set

The evidence axis contains three runs:

- `verified-only`: only page-verified locality claims;
- `reviewed-baseline`: KEEP and accepted DOWNGRADE decisions;
- `inclusive`: the baseline plus disputed Ascalon and Tortosa in 1130, and Cairo and Jaffa in 1187.

The model axis holds the reviewed evidence constant and varies the solver:

- `flat-natural` removes the Mount Lebanon and Taurus costs;
- `projection-normal` and `projection-expansive` test the two other allowed projection ordinals against the contracted baseline;
- `grid-5km` and `grid-20km` bracket the 10 km baseline.

All eight named scenarios are defined in `scenario-config.json`. Their effective inputs and run manifests are regenerated before the figure is written.

## Classification

All outputs are rasterized to a common 10 km analysis grid. Four classes are reported:

- **stable core**: evidence scenarios and model scenarios are each unanimous on the same non-zero entity;
- **model-sensitive zone**: evidence scenarios agree, while at least one model variant changes the assignment;
- **evidence-sensitive zone**: model scenarios agree, while evidence scenarios change the assignment;
- **unresolved zone**: both groups vary, the two unanimous groups disagree, or assignment exists only on one axis.

Cells unassigned by every scenario are reported separately and left uncolored.

## Results

### 1130

The assessed surface contains 13.65% stable core, 81.59% model-sensitive area, 1.31% evidence-sensitive area, and 3.46% unresolved area. Mean within-axis agreement is 0.9841 for the evidence scenarios and 0.7128 for the model scenarios.

The large model-sensitive share is driven mainly by the allowed projection ordinals, especially the expansive run, rather than by the two disputed localities. Evidence sensitivity is concentrated around the Ascalon/Fatimid and Tortosa additions. The Edessa downgrade affects baseline reach through its lower seed weight and remains part of the research judgment.

### 1187

The assessed surface contains 12.98% stable core, 75.44% model-sensitive area, 2.36% evidence-sensitive area, and 9.22% unresolved area. Mean agreement is 0.9614 on the evidence axis and 0.7191 on the model axis.

Cairo adds a large southwestern field in the inclusive run, while Jaffa changes a smaller coastal area. Their interaction with the projection and grid variants creates the larger unresolved share. The stable cores remain close to the reviewed locality anchors; this stability belongs to the current scenario design and carries no probability meaning.

## Reading the figure

`uncertainty-zones.png` uses categorical colors. A green cell means every run in both scenario groups assigned the same entity. Orange and purple identify which axis caused disagreement. Red marks cells where one-axis attribution would be misleading.

The area values use the 10 km analysis grid, so each counted cell contributes 100 km². They are scenario diagnostics, not measured medieval territorial areas.

## Limits and human review

The scenario set is deliberately small and structured. It does not sample every plausible historical interpretation, calibration, natural feature, or date convention. A historian must still decide whether the downgraded and disputed inputs are admissible and whether the projection range is a useful model stress test.
