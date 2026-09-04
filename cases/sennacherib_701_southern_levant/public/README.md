[English](README.md) | [简体中文](README.zh-CN.md)

# Sennacherib 701 Southern Levant Prospective Case

**Strict preregistration · completed_no_reconstruction · held-out material permanently sealed**

This prospective case studies the Joppa–Ekron–Lachish–Jerusalem corridor during the conventionally dated **701 BCE third-campaign and direct-disposition horizon**. The horizon is not a day-level snapshot. Time is stored with explicit BCE era/year fields; astronomical year `-700` is computational only.

## Terminal decision

The limited audit returned **GO for preregistration and evidence collection**. The frozen reconstruction gate subsequently returned **NO-GO**, so the case is complete without reconstruction. The post-freeze round used 16 of 24 queries, all 20 permitted content/record checks and 7 of 12 source admissions. Every registered gap received both permitted directed follow-up rounds.

Five candidate entities have textual paths: Judah, Ekron, Ashdod, Gaza and Ashkelon. Twelve locality candidates are fixed: Joppa, Ekron, Lachish, Jerusalem, Ashdod, Gaza, Ashkelon, Bīt-Daganna/Beth-Dagon, Banayabarqa/Bene-Baraq, Azuru, Eltekeh and Timnah. None is currently an allocation seed.

The gate failed because no two entities each have two independent, legally accessible and horizon-applicable named-locality local-control relations. Judah and Ekron each have at most one eligible point. Ashkelon has several named relations in one partisan royal lineage. Ashdod and Gaza receive unnamed towns only. The modeled entity roster is therefore empty.

## Evidence boundary

Assyrian conquest, tribute, suzerainty, military presence, local dynastic rule, transfer, destruction and local administration remain separate. ORACC parallel witnesses are one partisan royal lineage. Lachish destruction is an event observation, not a control relation. The Hebrew Bible path remains excluded from independent-corroboration counts until textual layer, composition and dependency are reviewed.

The reviewed round closes the destruction-chronology and biblical-lineage gaps with explicit constraints, closes the unnamed Ashdod and Gaza transfers as exclusions, and closes the Judah, Ashkelon, Ekron and locality-identification gaps unresolved. No coordinate layer, land mask, DEM, route, hydrography or archaeology point layer was acquired. No scenario solver, sensitivity run, polygon, territorial surface or reconstruction output exists; model dominance is not applicable because no model ran.

## Prospective seal

*The Carta Bible Atlas* is registered by bibliographic metadata only. The *Oxford Bible Atlas* and *The Bible Atlas* are excluded because search results exposed a cover thumbnail or map-label summaries. No historical territorial map body, plate, PDF map page, screenshot, OCR, vector or derivative was opened or stored.

The first Git freeze still binds the original nine machine-readable artifacts byte-for-byte. Post-freeze evidence is preserved in the append-only reviewed round and its SHA-256 manifest. Because the reconstruction gate failed, no `reconstructed_pre_evaluation` freeze exists and held-out content cannot be opened for this case.

## Files

- [Feasibility audit](feasibility-audit.md) and [Simplified Chinese version](feasibility-audit.zh-CN.md)
- [Human-readable preregistration](PREREGISTRATION.md) and [Simplified Chinese version](PREREGISTRATION.zh-CN.md)
- `preregistration.json`: frozen question, scope, ontology, budgets, gates and evaluation units
- `research-bundle.json`: disclosed pre-freeze Source → Observation → Claim → Model Decision state
- `held-out-map-register.json`: sealed bibliographic metadata only
- `spatial-input-contract.json`: twelve locked locality candidates and no-input/no-polygon gate
- `preregistration-freeze.json`: SHA-256 manifest
- `research/rounds/01-non-map-evidence/`: exact queries, source checks, observations, claims, decisions, gap outcomes, budget, gate and SHA-256 manifest
- `lifecycle.json`: append-only lifecycle ending at `completed_no_reconstruction`

Validate without reconstructing:

```bash
historical-geo validate cases/sennacherib_701_southern_levant/public
```
