[English](README.md) | [简体中文](README.zh-CN.md)

# Evidence-Driven Historical Geography

**Auditable spatial research agent prototype · Python 3.9+ · backend-neutral research contracts · two reproducible historical slices**

This project tests whether a research agent can build an acceptable historical-geography hypothesis from scattered, heterogeneous, and conflicting evidence without reading an existing territorial map. The system keeps the agent's epistemic state explicit, compiles eligible decisions into a backend-neutral spatial request, diagnoses where the resulting hypothesis is sensitive, and turns consequential evidence gaps into the next search agenda.

![1130 and end-of-1187 boundary hypotheses](cases/crusader_states/public/figures/reconstruction-slices.png)

```mermaid
flowchart LR
    A[Evidence search] --> B[Epistemic state]
    B --> C[Spatial hypothesis]
    C --> D[Uncertainty diagnosis]
    D --> E[Ranked search targets]
    E --> A
    C --> F[Held-out evaluation]
```

## What the agent does

For each case, the agent works through a research loop:

```text
search and retrieve sources
  -> record observations with locators and rights
  -> reconcile or preserve conflicts
  -> classify claims by spatial meaning
  -> make reviewed model decisions
  -> compile a backend-neutral spatial hypothesis
  -> compare controlled evidence and model scenarios
  -> diagnose consequential uncertainty
  -> rank the next evidence searches
```

This repository supplies the contracts, executable checks, case structure, and failure rules for that loop. Source retrieval can be performed by any capable research agent. Irreducible historical decisions remain visible for human acceptance.

## Why the separation matters

A source may establish that a city changed hands, a ruler used a political title, or an army followed a route. Those observations do not establish a continuous territorial boundary. The lineage keeps sources, observations, claims, model decisions, solver inputs, and output features separate so an agent cannot silently promote one kind of evidence into another.

The v0.2 contract treats `Source → Observation → Claim → Model Decision → Evidence Gap` as the agent's epistemic state. The compiler exposes only generic roles such as control points, spatial constraints, and traversal constraints. XTENT is one replaceable backend behind that boundary.

## Flagship case: Crusader States

The case covers **1130** and **end of 1187**. Round 01 closes the Cairo, Jaffa, Edessa-date, and Tripoli-inland gaps through page-addressable text and gazetteer evidence; it admits Cairo and Jaffa as locality points and adds Rafaniyya as a minor 1130 control point. These changes remain locality constraints, never direct county or state perimeters. The Ascalon gap remains open and its disputed anchor stays an evidence scenario.

The frozen claim-decision register and the round-specific state-change record keep these judgments machine-readable. They record the source/observation/claim/decision delta instead of leaving a revised baseline in prose alone.

![Evidence-backed locality anchors](cases/crusader_states/public/figures/evidence-anchors.png)

## External comparison

The project registers four published maps from three works. Public-domain Shepherd and Johnston plates support a categorical comparison; Buck’s exact 1130 map is recorded as access- and rights-blocked because the legal preview does not expose the map body. No scan or traced atlas boundary is committed.

The comparison checks named city control, entity presence, adjacency, and coastal place order. It reports 12 of 17 comparable assertions aligned for the c.1140 proxy, 4 of 4 entity assertions aligned for Shepherd’s c.1190 plate, and 13 of 14 city/entity assertions aligned for Johnston’s 1187–1190 campaign map. These counts describe agreement, not historical accuracy.

![Categorical external map comparison](cases/crusader_states/public/figures/reference-comparison.png)

## Uncertainty-driven research

Eight scenarios test evidence eligibility, natural costs, the allowed projection ordinals, and 5/10/20 km grids. Their common analysis grid separates stable core, model-sensitive, evidence-sensitive, and unresolved zones.

![Scenario agreement zones](cases/crusader_states/public/figures/uncertainty-zones.png)

The large model-sensitive share shows that bounded projection choices dominate the current areal result. The v0.2 diagnosis also measures which evidence scenarios change the assignment and links those changed cells back to open evidence gaps. Round 00 ranks the first concrete searches; round 01 records which gaps were closed and recomputes the residual agenda.

The Crusader case is a retrospective testbed: external maps never enter reconstruction inputs or parameter tuning, although they were already inspected during development. A future case is required for a strict pre-registered held-out evaluation.

## Research rounds and policy experiment

`research/rounds/00-initial/` preserves frozen pre-search bundle/scenario snapshots together with the diagnosis and agenda; `research/rounds/01-evidence-update/` preserves its source checks, state changes, and recomputed slice diagnoses. A reviewed round records the source/observation/claim/decision delta together with the diagnosis and search targets that justified the next action; transient solver runs remain under ignored `build/` directories. Canonical hashes bind the before/after snapshots to the round delta.

`research/experiments/equal-budget-policy/` contains a **constructed deterministic replay** of targeted, fixed-order, and broad-order search policies at equal budget. Its declared fixture outcomes appear in the input and result files. The experiment verifies selection and accounting mechanics only; it does not demonstrate that one policy improves real historical research.

## Implemented components

| Component | Role |
|---|---|
| Auditable epistemic state | Keeps source, observation, claim, decision, and evidence gap distinct. |
| Backend-neutral compiler | Selects reviewed decisions and creates a generic reconstruction request. |
| XTENT backend | Translates generic roles into deterministic XTENT solver inputs. |
| Cost-distance reconstruction | Produces valid, non-overlapping territorial surfaces on a projected grid. |
| Uncertainty diagnosis | Separates evidence effects from model sensitivity at grid-cell level. |
| Search-target generator | Ranks only open gaps with observed spatial consequences. |
| Comparative evaluation | Compares external maps without treating them as ground truth or tuning targets. |

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'

.venv/bin/historical-geo validate cases/crusader_states/public
.venv/bin/historical-geo compile-request cases/crusader_states/public \
  --slice 1130 --scenario reviewed-baseline
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/public --slice 1130
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo research-loop \
  cases/crusader_states/public --slice 1130
.venv/bin/historical-geo policy-experiment \
  cases/crusader_states/public/research/experiments/equal-budget-policy/experiment.json
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo figures \
  cases/crusader_states/public
.venv/bin/pytest
```

`validate`, `compile-request`, `reconstruct`, and `run` use the v0.2 epistemic-state compiler followed by the XTENT backend. The hash-frozen v0.1 adapter survives only through `legacy-*` commands for regression fixtures. Generated runs remain under ignored `build/` directories. Reviewed figures and machine-readable metrics are kept under `cases/crusader_states/public/figures/`.

## Verified state

- CI runs the full test suite on supported Python versions.
- The legacy v0.1 baseline is hash-frozen before migration.
- The v0.2 bundle, diagnosis, and search-target documents pass structural and referential validation.
- Backend-boundary tests show that the frozen round-00 v0.2 snapshots reproduce the reviewed v0.1 XTENT baseline; round 01 then records and hashes its intentional input and surface changes.
- Public lineage validation reports zero errors.
- Required scenarios for both slices rebuild successfully.
- Every run retains its expected scenario entities; geometry is valid and non-overlapping.
- Six figures pass nonblank QA.
- Fixture byte counts and SHA-256 hashes match.
- Paired English/Chinese headings and relative links pass repository checks.
- No cache, absolute machine path, source PDF, atlas scan, restricted map derivative, or unexpected large file is present in the public tree.

These checks establish reproducibility and auditability. Historical acceptance still requires a qualified reader.

## Documentation

- [Methodology and agent research protocol](docs/architecture/methodology.md)
- [Crusader States case study](docs/research/crusader-states-case-study.md)
- [Historical source review](docs/research/source-review.md)
- [Comparative evaluation](docs/research/comparative-evaluation.md)
- [Uncertainty analysis](docs/research/uncertainty-analysis.md)
- [Reproducibility guide](docs/operations/reproducibility.md)
- [Fixture attribution and rights](cases/crusader_states/public/ATTRIBUTION.md)
- [Software license](LICENSE) and [data/content terms](DATA-LICENSE.md)
