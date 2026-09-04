[English](README.md) | [简体中文](README.zh-CN.md)

# Sennacherib 701 Southern Levant Prospective Case

**Strict preregistration · evidence_collection · reconstruction blocked · held-out material sealed**

This prospective case studies the Joppa–Ekron–Lachish–Jerusalem corridor during the conventionally dated **701 BCE third-campaign and direct-disposition horizon**. The horizon is not a day-level snapshot. Time is stored with explicit BCE era/year fields; astronomical year `-700` is computational only.

## Feasibility decision

The limited audit returns **GO for preregistration and evidence collection** and **NO-GO for reconstruction at this stage**. It logged exactly 12 queries, 10 text/catalog access attempts, six preliminary sources and one metadata-only held-out candidate.

Five candidate entities have textual paths: Judah, Ekron, Ashdod, Gaza and Ashkelon. Twelve locality candidates are fixed: Joppa, Ekron, Lachish, Jerusalem, Ashdod, Gaza, Ashkelon, Bīt-Daganna/Beth-Dagon, Banayabarqa/Bene-Baraq, Azuru, Eltekeh and Timnah. None is currently an allocation seed.

## Evidence boundary

Assyrian conquest, tribute, suzerainty, military presence, local dynastic rule, transfer, destruction and local administration remain separate. ORACC parallel witnesses are one partisan royal lineage. Lachish destruction is an event observation, not a control relation. The Hebrew Bible path remains excluded from independent-corroboration counts until textual layer, composition and dependency are reviewed.

The baseline bundle contains only display and exclusion decisions. No coordinate layer has been acquired and no polygon, territorial surface or reconstruction output exists.

## Prospective seal

*The Carta Bible Atlas* is registered by bibliographic metadata only. The *Oxford Bible Atlas* and *The Bible Atlas* are excluded because search results exposed a cover thumbnail or map-label summaries. No historical territorial map body, plate, PDF map page, screenshot, OCR, vector or derivative was opened or stored.

The first Git freeze binds nine machine-readable artifacts. A second `reconstructed_pre_evaluation` freeze is mandatory before any held-out body can be opened. If the reconstruction gate fails, the case must terminate as `completed_no_reconstruction` and keep the atlas sealed.

## Files

- [Feasibility audit](feasibility-audit.md) and [Simplified Chinese version](feasibility-audit.zh-CN.md)
- [Human-readable preregistration](PREREGISTRATION.md) and [Simplified Chinese version](PREREGISTRATION.zh-CN.md)
- `preregistration.json`: frozen question, scope, ontology, budgets, gates and evaluation units
- `research-bundle.json`: disclosed pre-freeze Source → Observation → Claim → Model Decision state
- `held-out-map-register.json`: sealed bibliographic metadata only
- `spatial-input-contract.json`: twelve locked locality candidates and no-input/no-polygon gate
- `preregistration-freeze.json`: SHA-256 manifest
- `lifecycle.json`: append-only lifecycle binding to the preregistration commit

Validate without reconstructing:

```bash
historical-geo validate cases/sennacherib_701_southern_levant/public
```
