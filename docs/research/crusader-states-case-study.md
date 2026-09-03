[English](crusader-states-case-study.md) | [简体中文](crusader-states-case-study.zh-CN.md)

# Crusader States Case Study

## Scope

This case tests an agent-led evidence-to-spatial-hypothesis loop on two bounded slices: **1130** and **end of 1187**. Existing historical boundary maps are withheld during evidence acquisition. They are registered only for later evaluation.

The checked-in epistemic state contains 23 sources, 63 observations, 23 claims, 33 model decisions, and nine evidence gaps. Each locality must pass through a source, an observation, a claim, and an explicit model decision before it can affect the XTENT backend. The repository stores citations, short project paraphrases, attributed approximate coordinates, clipped public-domain physical vectors, and machine-readable review records. It does not redistribute source PDFs, atlas pages, or traced copyrighted geometry.

## Round 01: the first completed research loop

Round 00 diagnosed candidate evidence gaps with single-decision counterfactuals. Its frozen before-state is preserved as [`research-bundle.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-bundle.snapshot.json) and [`research-scenarios.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-scenarios.snapshot.json); those snapshots reproduce the reviewed v0.1 solver inputs, while round 01 intentionally changes the current state. Cairo affected 1,162 grid cells, Edessa 257, Tripoli 220, Ascalon one, while Jaffa and Tortosa each affected zero. The agent therefore targeted Cairo, Edessa, and Tripoli. It did not select Ascalon. Jaffa was checked incidentally through the Cairo source trail, providing a zero-marginal control.

Round 01 made four bounded evidence changes:

| Gap | Evidence result | Epistemic-state change |
|---|---|---|
| Cairo in 1187 | Lane-Poole p. 219 names al-Adil marching from Cairo; Ibn Shaddad supplies Egyptian administrative and mobilization context. | Cairo changed from unresolved/disputed to a supported, admitted operational locality point. |
| Edessa in 1130 | Asbridge pp. 125–126 covers Joscelin's leadership through the section's 1130 endpoint; William of Tyre supplies adjacent-year corroboration. | The one-year bridge closed; Edessa remains admitted at minor weight. |
| Tripoli inland evidence in 1130 | Lewis bounds comital possession of Rafaniyya from 1126 to 1137; Syriaca.org supplies an approximate location. | Rafaniyya became a new supported, admitted minor control point. |
| Jaffa in 1187 | Lane-Poole states its capture; a contemporary letter is checked through Kauffeldt's mediated transcription. | Jaffa changed from unresolved/disputed to a supported, admitted locality point. Its isolated surface effect remains zero cells. |

The complete search record is [`source-checks.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/source-checks.json), and all object-level transitions are recorded in [`state-changes.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/state-changes.json). The held-out guard in the search record states that no historical boundary map was consulted.

## Current slice definitions

The 1130 reviewed baseline contains five modeled entities: the Kingdom of Jerusalem, Burid Damascus, the County of Tripoli, the Principality of Antioch, and the County of Edessa. Tripoli now has two locality constraints, Tripoli and Rafaniyya. Fatimid Egypt remains absent because Ascalon is still experimental; Tortosa is also experimental. The 1130 `inclusive` scenario adds only Ascalon and Tortosa.

The end-1187 reviewed baseline contains the Ayyubid Sultanate and surviving Latin centers represented by the Kingdom of Jerusalem at Tyre, the County of Tripoli, and the Principality of Antioch. Cairo and Jaffa are now admitted Ayyubid points in the baseline. Consequently, `verified-only`, `reviewed-baseline`, and `inclusive` coincide for 1187.

A point constrains its own locality and solver allocation. It does not establish a polity's perimeter, continuous occupation between points, or control of a surrounding region.

## Spatial response to the evidence update

The round-to-round reconstruction is quantified in [`round-delta.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/round-delta.json). With the declared 10 km analysis grid and current XTENT ordinal backend:

- In 1130, adding Rafaniyya changed **0 of 13,924** analysis-grid assignments. The point improved the audit state without changing this backend's surface.
- In 1187, admitting Cairo and Jaffa changed **1,162 of 13,924** analysis-grid assignments. Every transition was from unassigned to Ayyubid Sultanate. Cairo accounts for this response; Jaffa's isolated marginal effect is zero.

These counts measure backend response to audited state changes. They do not measure historical accuracy or validate a boundary.

The reconstruction, anchor, natural-ablation, and attractor figures under [`cases/crusader_states/public/figures`](../../cases/crusader_states/public/figures/README.md) are regenerated from the current round-01 v0.2 state. The external-map comparison and grouped scenario-agreement figure remain explicitly frozen at round 00 so the held-out evaluation record is not silently rewritten.

## Current uncertainty diagnosis

The updated 1130 diagnosis assigns one evidence-sensitive cell to the still-experimental Ascalon decision; Tortosa has zero isolated effect. Model alternatives affect 5,823 cells. Its only next evidence-search target is Ascalon.

The updated 1187 diagnosis contains no evidence-axis intervention because all admitted locality decisions now meet the project's page-checked threshold. Model alternatives affect 5,269 cells, so the slice is classified as model-sensitive and produces no evidence-search target. The diagnoses are [`uncertainty-diagnosis-1130.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1130.json) and [`uncertainty-diagnosis-1187.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1187.json).

Mount Lebanon and Taurus remain explicitly assumption-labeled friction features. The Jordan River remains display context and a rejected boundary-attractor candidate. These are model decisions, not historical boundary evidence.

## Open questions and human review boundary

Five gaps remain open: Ascalon in 1130, Tortosa in 1130, the extent of surviving Latin holdings at end of 1187, and reach-class sensitivity in both slices. The first two can trigger bounded evidence searches; the survival-extent gap seeks additional localities or routes; the two reach gaps require model diagnosis rather than source search alone.

Closing a workflow gap does not settle its historiography. A historian must still judge whether the cited secondary passage and contextual primary material justify Cairo as an operational point, whether the mediated contemporary letter and Lane-Poole justify Jaffa under the exact year-end convention, whether Asbridge's treatment adequately resolves Edessa for 1130, and whether Rafaniyya's dated possession and approximate gazetteer coordinate justify a minor solver seed. The project claims auditable locality-level inputs and explicit backend consequences, not recovered historical borders.
