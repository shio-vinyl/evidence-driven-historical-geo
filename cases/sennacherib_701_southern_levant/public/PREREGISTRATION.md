[English](PREREGISTRATION.md) | [简体中文](PREREGISTRATION.zh-CN.md)

# Preregistration

## Frozen question and scope

The case asks which named localities in the Joppa–Ekron–Lachish–Jerusalem corridor can be supported as local-control points, transfer objects, contested places or unresolved localities of Judah, Ekron, Ashdod, Gaza and Ashkelon during Sennacherib’s conventionally dated **701 BCE third-campaign and direct-disposition horizon**.

Time is stored as `calendar=historical_bce_year_label`, `era=BCE`, `year_bce=701`, and `temporal_resolution=campaign_horizon`. Astronomical year `-700` follows `astronomical_year = 1 - year_bce` and exists only for computation; a negative ISO date is prohibited. The horizon does not assert that the operations were simultaneous or day-resolved. The WGS84 box is `[34.0, 30.7, 35.5, 32.5]`.

## Evidence and ontology

Allowed inputs are line-addressable cuneiform editions, excavation and dating reports, local inscriptions, critically described Hebrew textual witnesses, licensed gazetteers, site coordinates, terrain, routes and hydrography. Existing territorial maps and every body, thumbnail, plate, screenshot, OCR, vector or derivative remain prohibited before the evaluation gate.

The ontology keeps local dynastic rule, contested authority, transfer, Assyrian conquest, tribute, suzerainty, military presence, destruction and local administration separate. Only a supported, named, horizon-applicable local-administration claim can authorize a control point. Parallel Assyrian witnesses and translations remain one partisan royal lineage unless source criticism demonstrates otherwise. Hebrew Bible material must preserve textual layer, composition and dependency uncertainty.

Every admission follows `Source → Observation → Claim → Model Decision`. A source statement cannot skip a layer. Unnamed transferred towns never acquire invented coordinates.

## Search and reconstruction gate

Post-freeze evidence collection is limited to 24 logged queries, 20 content-record checks, 12 source admissions, two follow-ups per gap, four held-out metadata queries and three held-out candidates. A gap stops when its success criterion is met or two follow-ups add no admissible evidence.

Reconstruction requires at least two entities with two independent, legally accessible, horizon-applicable named-locality local-control relations each; ten locatable candidates from four independent source lineages; two retained counterevidence or exclusion relations; and stable locators and rights for every admission. Failure produces `NO_RECONSTRUCTION`, never a speculative polygon.

## Held-out evaluation

Candidate order and twenty categorical evaluation units are frozen in `preregistration.json`. Every unit receives `aligned`, `not_aligned`, `not_expressed` or `not_comparable`; the denominator cannot shrink after opening. Fewer than eight expressed comparable units makes the comparator inconclusive.

The atlas body stays sealed until a second `reconstructed_pre_evaluation` Git commit freezes the effective evidence state, scenarios, code, calibration, outputs, place coordinates, rubric and hashes. Held-out content can never flow back into evidence or tuning.

## Amendment and limits

Any post-freeze amendment must be versioned and committed before the affected analysis. After held-out content is opened, changes are post hoc and cannot replace the preregistered result.

The current evidence is concentrated in partisan Assyrian reports. Ashdod and Gaza receive unnamed places; several site identifications remain open; the biblical path is source-critical; the atlas may express too few units. Repository checks establish artifact isolation and declaration consistency, not a complete human browsing history.
