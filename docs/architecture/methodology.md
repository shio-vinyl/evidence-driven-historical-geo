[English](methodology.md) | [简体中文](methodology.zh-CN.md)

# Methodology and Architecture

## Design objective

The system produces auditable territorial reconstruction hypotheses while keeping historical evidence, modeling assumptions, solver behavior, and cartographic presentation distinct.

A generated polygon is not expected to have a fictitious one-to-one source citation. Its influencing observations, reviewed anchors, friction inputs, transformation rules, run settings, and unresolved gaps must still be recoverable.

## Agent research loop

The intended operator is a research agent. It should search catalogs and legal repositories, retrieve page-addressable material, record access and rights, compare accounts, and decide how each claim may be used. When sources conflict, the agent must narrow the claim, downgrade it, remove it, or preserve it in a disputed scenario. A solver default is never an acceptable resolution of a historical disagreement.

The repository provides the protocol and executable guardrails for that work. It does not ship an autonomous browsing runtime. Source discovery happens through the agent's available tools; the resulting observations, decisions, and access records are saved in the case. Human review remains necessary where chronology, translation, or political interpretation cannot be settled from the checked material.

The agent's operation grammar is: **search → structure claims → compile a spatial hypothesis → diagnose uncertainty → target the next search**. Each transition writes a reviewable object. The current hypothesis therefore changes the next research action instead of ending the workflow.

## Epistemic boundary

The method distinguishes five statements that conventional mapping workflows often collapse:

1. a source contains a report;
2. the report supports a historical claim;
3. the claim is eligible for a spatial modeling role;
4. the model produces a territorial surface;
5. the surface is displayed as a boundary hypothesis.

A true statement at one level does not automatically authorize the next level. A battlefield can be historically well attested and still be rejected as a territorial seed. A modern river centerline can be spatially accurate and still lack evidence for a historical boundary role.

## Prospective held-out cases

A prospective case has a lifecycle separate from reconstruction: `preregistered → evidence_collection`, followed either by `reconstructed_pre_evaluation → evaluation_opened` or by the terminal `completed_no_reconstruction` state. Before evaluation, held-out historical maps remain in a metadata-only register and cannot appear in sources, observations, claims, model decisions, scenarios, or spatial inputs. A Git commit freezes the preregistration; a second commit must freeze evidence, model settings, outputs, fixed comparison units, and hashes before the first map body is opened. A terminal negative result never opens the held-out material.

Repository validation rejects held-out identifiers in research artifacts, map-body files and premature boundary outputs in a sealed case, and mismatches against the frozen-artifact hash manifest. This establishes artifact isolation and a checkable declaration. It cannot establish a complete human browsing history, so any accidental snippet or preview exposure must be disclosed and the affected candidate excluded or marked contaminated.

## Era-aware BCE time contract

BCE prospective cases do not use negative ISO dates. They store a calendar label, `era=BCE`, a positive `year_bce`, the evidence resolution, a horizon definition, chronology uncertainty, and an explicit astronomical-year conversion. For a BCE year `n`, the conversion is `astronomical_year = 1 - n`; therefore 701 BCE corresponds to astronomical year `-700`, and 1 BCE corresponds to astronomical year `0`.

`campaign_horizon` is an evidentiary resolution, not a calendar instant. It can group operations and directly reported dispositions conventionally assigned to one campaign while preserving uncertainty about sequence, synchronism and composition. The validator checks the conversion and rejects negative ISO-shaped substitutes. Public research records retain the historical era/year representation even when a spatial or numerical backend needs astronomical numbering.

## Append-only prospective evidence rounds

A prospective freeze remains byte-for-byte immutable after preregistration. Later research lives in `research/rounds/<round-id>/` as source, observation, claim, decision, gap and budget deltas. `lifecycle.json` binds the frozen manifest and preregistration commit to reviewed round manifests; the current state is materialized from the baseline plus those deltas rather than by rewriting the baseline bundle.

Validation recomputes every round-file hash, checks the previous-state chain and exact file set, rejects duplicate epistemic IDs, verifies cross-record references and source-access fields, accounts for queries, record checks, admissions and per-gap follow-ups, enforces legal stage transitions, and scans all round artifacts for held-out identifiers. A failed reconstruction gate enters the terminal `completed_no_reconstruction` state and forbids later rounds or polygon output. The hash chain is tamper-evident inside the repository and gains durable immutability from Git history.

The completed Mercia–Welsh case is the strict preregistered negative-result path in operation. Its 780–796 locality-level political-control evidence did not satisfy the reconstruction gate, so budget control and the stop rule ended the case without geometry while the held-out atlas remained permanently sealed. This outcome demonstrates successful execution of the protocol under insufficient evidence; it is not a project failure and is not a historical-accuracy result.

## End-to-end workflow

```text
source
  -> observation
  -> evidence claim
  -> reviewed model decision
  -> backend-neutral reconstruction request
  -> spatial backend input
  -> reconstruction run
  -> output feature
  -> uncertainty diagnosis
  -> ranked evidence search targets
```

The default command path is:

```text
validate -> compile-request -> reconstruct/run -> research-loop
```

`validate`, `compile-request`, `reconstruct`, and `run` compile the v0.2 epistemic state before crossing the XTENT backend boundary. The hash-frozen v0.1 adapter is available only through explicit `legacy-*` commands for regression fixtures. `historical-geo figures` preserves the baseline and ablation figure checks.

## Core data model

| Object | Meaning |
|---|---|
| Source | A citable text, dataset, map, gazetteer, or synthetic fixture. |
| Observation | A statement, event, measurement, or location directly read from a source. |
| Evidence claim | A reviewed historical interpretation with entity, time, spatial meaning, status, and observation references. |
| Model decision | The explicit, backend-neutral translation of evidence—or a declared assumption—into a bounded modeling instruction. |
| Spatial anchor | A reviewed locality point allowed to enter allocation. |
| Historical phase | One entity's modeled state during a defined interval. |
| Reconstruction run | Effective inputs, calibration version, processing metadata, and hashes. |
| Boundary hypothesis | Model-derived geometry carrying provenance and limitations. |
| Research gap | An unresolved item with a question, evidence strategy, success criterion, and stop condition. |
| Search target | An open gap promoted to the next research round because a controlled evidence scenario changed the current spatial hypothesis. |

The v0.2 JSON contracts live in `schemas/`. Structural JSON Schema validation is supplemented by referential and semantic checks in `historical_geo.research_contracts`.

## Compiler and backend boundary

The research compiler converts reviewed decisions into a deterministic reconstruction request without importing XTENT vocabulary. Its generic roles include:

- control points;
- spatial constraints;
- traversal constraints;
- explicit exclusions;
- display-only context.

Every scenario carries an explicit control-point allowlist. An empty allowlist means that no control points are selected; it never falls back to every admitted point. Admitted spatial/traversal assumptions remain active unless explicitly excluded.

The XTENT backend translates the supported subset into seeds, phases, and friction features. Another spatial inference backend can consume the same epistemic state through its own translator.

The public contract uses bounded ordinal choices instead of unrestricted model tuning. Phase reach is represented by named projection classes; natural polygon costs use `hard`, `soft`, or `porous` roles. The numerical values behind those classes belong to the model calibration, not to historical sources.

The compiler and backend fail before reconstruction when they encounter:

- missing evidence or source references;
- non-areal relations entering allocation without authorization;
- unknown seed coordinates;
- display-only records leaking into allocation;
- unsupported natural-feature roles;
- raw tuning values where a bounded ordinal is required.

## Uncertainty diagnosis and search policy

Evidence scenarios and model scenarios are compared to the reviewed baseline on a common assignment grid. Changed cells are attributed to the decisions varied by each scenario. The diagnosis reports `evidence_gap`, `model_sensitivity`, or `mixed` for each slice and never interprets the cell count as probability.

An open evidence gap becomes a search target only when an evidence-axis scenario linked to that gap changes the spatial assignment. Targets are ranked by affected cells and explicit decision linkage. Each target records a research question, preferred source types, success criteria, and a stopping condition. Pure model sensitivity produces a modeling finding and cannot manufacture a literature search.

## Reconstruction engine

### Projected grid

Fixture geometry and locality points are stored in WGS84. Land, natural features, and seeds are transformed into the configured Lambert conformal conic grid before rasterization. The public case uses a 10 km working grid.

Approximate coastal seeds that land in a water cell can move deterministically to the nearest land cell within three cells. Conflicting entity seeds in one cell fail explicitly.

### Cost-distance allocation

The XTENT core builds a friction surface and calculates least-cost influence from reviewed anchors. Only cells with positive influence are allocated. A reviewed `point_control` claim retains ownership of its raster cell even when a stronger neighboring field would otherwise erase it; this preserves the point observation without granting an artificial surrounding footprint.

### Materialization and topology

Allocated cells are vectorized into entity surfaces, clipped to the land mask, and checked for validity and exclusive coverage. Nonlinear reprojection can create small shared-edge overlaps in WGS84, so the pipeline restores exclusivity in deterministic entity order and fails if validity, non-overlap, or entity retention is false.

## Natural-feature experiment

Modern geometry supplies location, not historical meaning. A natural feature can influence allocation only through a reviewed historical role or an explicit model assumption.

The public case uses:

- Mount Lebanon: `soft` polygon cost, assumption;
- Taurus Mountains: `porous` polygon cost, assumption;
- Jordan River: display context only.

The `flat` scenario removes both mountain-cost decisions. Baseline/flat symmetric difference is measured in equal-area `ESRI:102025`. It quantifies model sensitivity; it is not an accuracy score.

## Guarded boundary alignment

`historical_geo.attractors.align_shared_boundary` evaluates one shared edge against a candidate vector. It never snaps entity polygons independently. Acceptance requires all configured guards to pass:

- proximity;
- direction similarity;
- maximum displacement;
- bounded area change;
- entity retention;
- valid geometry;
- no overlap;
- coverage preservation.

The public diagnostics contain a near-parallel synthetic candidate that passes and a real Jordan River candidate that fails direction similarity (`0.0209` against a required `0.8`). A rejected candidate leaves the source geometry unchanged.

## Validation and provenance

Validation covers:

- JSON structure and identifier references;
- evidence eligibility and assumption labeling;
- expected entity retention;
- geometry validity and non-overlap;
- land-mask containment;
- effective-input and output hashes;
- attractor diagnostics;
- nonblank and semantic figure QA;
- fixture licenses and source checks.

Every public run writes its effective solver input and a run manifest. Research gaps remain visible rather than being converted into arbitrary geometry.

## Implementation map

| Module | Responsibility |
|---|---|
| `research_contracts.py` | v0.2 epistemic-state, diagnosis, and search-target validation |
| `compiler.py` | Reviewed decisions to a backend-neutral reconstruction request |
| `backends/xtent_backend.py` | Generic request to deterministic XTENT solver input |
| `diagnosis.py` | Scenario attribution and next-search ranking |
| `research_case.py` | Case-level compile, run, and research-loop orchestration |
| `contracts.py` / `adapter.py` | Frozen v0.1 compatibility and regression baseline |
| `xtent.py` | Cost-distance influence and allocation |
| `pipeline.py` | Projection, friction, vectorization, lineage, hashes, and QA |
| `attractors.py` | Guarded shared-edge alignment |
| `render.py` / `figures.py` | Static output, diagnostics, and figure QA |

The XTENT allocation core was recovered from an earlier compiler experiment. Public lineage, adapter, orchestration, boundary-attractor, render, and fixture code were written against the current public contract; legacy paths, private data, and the old production driver were not carried forward.

## Deliberate limits

- No full scanned-atlas extraction pipeline.
- No automatic conversion of every historical relation into area.
- No claim that rivers or mountains are universal political barriers.
- No historical accuracy benchmark against a reference map that influenced model construction.
- No continuous-change model between the two case slices.
