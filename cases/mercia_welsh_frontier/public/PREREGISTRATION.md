[English](PREREGISTRATION.md) | [简体中文](PREREGISTRATION.zh-CN.md)

# Preregistration

## Frozen question and scope

The case asks which named localities in the Rhuddlan–upper Severn corridor can be classified as Mercian-controlled, controlled by a named Welsh polity, contested, or unresolved from non-territorial-map evidence during 780-01-01 through 796-07-29. A later reconstruction, if permitted, will test sensitivity to explicit treatments of Offa's Dyke. The target is an interval because most events are only year-resolved; it is not a political snapshot precise to 29 July 796.

The WGS84 bounding box is `[-3.65, 52.05, -2.65, 53.40]`. Mercia, Powys, and Gwynedd are candidate entities. A candidate remains unresolved until the frozen admission threshold is met; “Britons” cannot be compiled as a single Welsh state.

## Evidence and lineage

Allowed inputs are locatable texts, charters with authenticity notes, archaeology and scientific dating, historic-environment records, licensed gazetteers, terrain, hydrography, routes, settlements, place-name work, and other non-territorial-map material. Existing historical territorial maps, their bodies or derivatives, and model defaults presented as evidence are prohibited.

Every admitted path must remain `Source → Observation → Claim → Model Decision`. One observation records one source statement or measurement. Events, titles, raids, tribute, battles, engineering locations, and point control do not authorize continuous territorial extent. Only a supported, interval-applicable claim may authorize an admitted decision.

## Offa's Dyke

Offa's Dyke is a contested feature with `political_boundary_equivalence=false`. Its default role is display context and the current scenario excludes it from allocation. A specified section may become a traversal constraint, corridor, disputed clue, or exclusion only after separate evidence supports that role. A hard political split is prohibited.

## Search and stopping rules

After the preregistration commit, the budget is 24 logged queries, 20 content-record inspections, 12 source admissions, two targeted follow-ups per gap, six held-out metadata queries, and three held-out candidates. Search stops at the first applicable condition: the reconstruction threshold is met; the budget is exhausted; a gap succeeds; or two targeted follow-ups add no admissible evidence.

Reconstruction requires at least two entities with two independent interval-applicable named-locality relations each, eight distinct spatial candidates from three independent source lineages, at least one retained counterevidence or exclusion relation, and stable locators and rights for every admission. Failure yields `NO_RECONSTRUCTION`, not a speculative polygon.

## Held-out evaluation

Candidate priority and thirteen categorical units are frozen in `preregistration.json`. Units are scored `aligned`, `not_aligned`, `not_expressed`, or `not_comparable`; the denominator cannot be reduced after opening. Fewer than six expressed comparable units makes the comparator inconclusive. Agreement is reported as agreement with one published map under a frozen rubric, never as historical accuracy.

The map body remains sealed until a second `reconstructed_pre_evaluation` commit freezes the evidence bundle, scenarios, code, calibration, reconstruction, place coordinates, rubric, and hashes. Held-out material can never flow back into research inputs or tuning.

## Frozen limits

The Welsh-side local evidence is currently sparse and often retrospective or just outside the interval. Rhuddlan's parties, outcome, and battlefield remain unresolved. Recorded dyke sections vary in continuity and dating, and their political function is not established. Binary allocation may erase a genuine unknown or frontier zone. Repository checks can show artifact isolation and declaration consistency but cannot prove a person's entire browsing history.
