[English](README.md) | [简体中文](README.zh-CN.md)

# Mercia–Welsh Frontier Prospective Case

**Completed strict preregistered negative result · completed_no_reconstruction · held-out material permanently sealed**

This strictly prospective case covers the Rhuddlan–Dee/Llangollen–Chirk–Oswestry/Llanymynech–upper Severn corridor during **780-01-01 through 796-07-29**. The interval closes with Offa's death; year-only evidence is not treated as day-precise.

## Final decision

The registered result is **`completed_no_reconstruction`**. This is the completed negative result of the frozen preregistration, not a provisional decision. Post-freeze non-map research found no modeled entity with the required two independent, legally accessible, interval-applicable named-locality political-control relations. Powys cannot be bridged from the ninth-century Pillar of Eliseg evidence, Gwynedd cannot be connected to the 796 Rhuddlan notice from the separate 798 royal notice, and Mercian title, occupation, battle and engineering evidence cannot establish continuous local control.

No polygon, territorial surface or reconstruction was generated. Offa's Dyke and Wat's Dyke remain outside allocation: broad or conflicting dates do not establish a target-interval role, and engineering location cannot stand for a political boundary.

## Reviewed evidence round

`research/rounds/01-non-map-evidence/` records 23 exact queries, 17 content or catalog checks, and 7 admitted sources. Each source check records its query, access date, URL, stable locator, content scope, rights, atomic observation, disposition, reason, lineage and related gap. Failed access attempts and rejected derivative records remain in the ledger.

The six gaps terminate as follows:

- `GAP_LOCAL_MERCIA_CONTROL`: **closed_unresolved**; no qualifying corridor locality relation was found.
- `GAP_POWYS_CONTINUITY`: **closed_unresolved**; the locatable evidence is ninth-century and retrospective.
- `GAP_GWYNEDD_CONTINUITY`: **closed_excluded**; the 798 notice cannot be merged with the 796 event.
- `GAP_RHUDDLAN_PARTIES`: **closed_unresolved**; parties, outcome, territorial consequence and exact battle site remain unsupported.
- `GAP_DYKE_DATE_AND_ROLE`: **closed_excluded**; no section meets both the dating and independently supported role requirements.
- `GAP_WATS_DYKE_RELATION`: **closed_excluded**; chronology conflicts or extends beyond the interval and function remains unresolved.

The gate retains twelve distinct spatial candidates, at least three independent source lineages, and explicit counterevidence/exclusions. It fails the two controlling criteria: at least two modeled entities, and two independent interval locality relations for each entity.

## Append-only lifecycle

`lifecycle.json` binds the immutable preregistration baseline at commit `94f8ee75662bf909f34796040d917a347e228662` to the reviewed round manifest. The effective case state is derived from that baseline plus reviewed deltas. Validation checks the round hash chain, the exact round file set, source/observation/claim/decision references, budget arithmetic, allowed stage transitions, effective gap state, held-out identifier isolation and the original nine freeze hashes.

## Prospective seal

The held-out register permanently remains bibliographic metadata only. No registered map body, thumbnail, PDF page, screenshot, OCR, vector or boundary geometry was inspected or stored. Because the reconstruction gate failed, no second pre-evaluation freeze exists and evaluation will never open the held-out atlas for this case outcome.

The workflow succeeded by enforcing evidence isolation, the preregistered budget, and the stop rule when the locality-level political-control evidence for 780–796 remained insufficient. The absence of a reconstruction is the protocol-prescribed negative result; it is not a project failure and supports no conclusion about historical accuracy.

Automated validation audits repository state and recorded declarations; it cannot prove a person's complete browsing history.

## Files

- [Human-readable preregistration](PREREGISTRATION.md) and [Simplified Chinese version](PREREGISTRATION.zh-CN.md)
- [Feasibility audit](feasibility-audit.md) and [Simplified Chinese version](feasibility-audit.zh-CN.md)
- `preregistration.json` and `preregistration-freeze.json`: immutable protocol and nine-artifact SHA-256 manifest
- `research-bundle.json`: immutable disclosed pre-freeze epistemic baseline
- `lifecycle.json`: append-only round chain and effective terminal state
- `research/rounds/01-non-map-evidence/`: query, source, observation, claim, decision, gap, budget and gate deltas
- `held-out-map-register.json`: sealed bibliographic metadata only

Validate without reconstructing:

```bash
historical-geo validate cases/mercia_welsh_frontier/public
```
