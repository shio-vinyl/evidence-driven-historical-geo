[English](README.md) | [简体中文](README.zh-CN.md)

# Mercia–Welsh Frontier Prospective Case

**Stage: evidence collection · conditional GO · reconstruction blocked**

This is the project's second case and its first strictly prospective held-out test. It covers the northern and central corridor from Rhuddlan through the Dee/Llangollen and Chirk–Oswestry/Llanymynech zones to the upper Severn during **780-01-01 through 796-07-29**. The interval closes with Offa's death; year-only evidence is not treated as day-precise.

## Current decision

The feasibility audit supports a conditional **GO** for preregistration and evidence collection. Mercia is directly documented inside the interval. Powys and Gwynedd are viable named research candidates, but their local interval control remains unresolved. The case therefore fails its present reconstruction gate and contains no territorial polygon.

Twelve named event, route, earthwork, terrain, chronology, or exclusion candidates are locatable. Their existence does not make them control points. In particular, Offa's Dyke is not equated with a political border: it is excluded from allocation and may enter only a separately justified future sensitivity scenario.

## Prospective seal

The held-out register contains bibliographic metadata only. No registered map body, thumbnail, PDF page, screenshot, OCR, vector, or boundary geometry has been inspected or stored. The primary comparator is fixed before evaluation. A second `reconstructed_pre_evaluation` Git commit must freeze evidence, scenarios, code, calibration, outputs, fixed coordinates, rubric, and hashes before any map body may be opened.

Automated validation checks the metadata-only flags, blocks held-out IDs from research artifacts, rejects map-body files and premature reconstruction outputs, and verifies the preregistration artifact hashes. These checks audit repository state and recorded declarations; they cannot prove a person's complete browsing history.

## Files

- [Human-readable preregistration](PREREGISTRATION.md) and [Simplified Chinese version](PREREGISTRATION.zh-CN.md)
- [Feasibility audit](feasibility-audit.md) and [Simplified Chinese version](feasibility-audit.zh-CN.md)
- `preregistration.json`: frozen machine-readable protocol
- `feasibility-audit.json`: machine-readable GO decision and constraints
- `research-bundle.json`: disclosed pre-freeze sources, observations, claims, decisions, and gaps
- `evidence-gap-register.json`: compact index whose authoritative records remain in the bundle
- `held-out-map-register.json`: sealed bibliographic metadata only
- `source-access-rights.json`: access, locator, and rights records
- `research-scenarios.json`: no-allocation baseline and future activation conditions
- `spatial-input-contract.json`: permissible spatial inputs and the no-polygon gate
- `preregistration-freeze.json`: SHA-256 manifest for frozen artifacts

Validate without reconstructing:

```bash
historical-geo validate cases/mercia_welsh_frontier/public
```
