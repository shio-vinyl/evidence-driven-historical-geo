[English](source-review.md) | [简体中文](source-review.zh-CN.md)

# Historical Source Review

## Review method

This case is built for a research agent. The agent searches catalogues, legal repositories, publisher pages, and page-addressable editions; records access and rights; writes a narrow paraphrase; then decides whether that record may enter a solver. A citation alone is insufficient. Conflicting or incomplete records remain visible in lineage and in the scenario register.

The unit of review stays narrow. A city-control statement can support a locality seed. A political title can identify a center without proving control of every named city. Events and routes remain observations. None of these proves a territorial perimeter by itself.

The repository contains no source scan, atlas page, long quotation, or copyrighted book text.

## Status definitions

- **Verified** — an accessible page or publisher record directly supports the stored locality-level paraphrase.
- **Partial** — the record supports only part of a grouped claim, a neighboring date, or a weaker political role.
- **Unresolved** — the load-bearing locator remains broad or the relevant locality is absent from the checked record.

`KEEP`, `DOWNGRADE`, `REMOVE`, and `DISPUTED` are input decisions, not alternative evidence statuses. The full record is machine-readable in [`historical-claim-decisions.json`](../../cases/crusader_states/public/historical-claim-decisions.json).

## Claim-level result

| Recovered claim | Review result | Page evidence and limit | Input consequence |
|---|---|---|---|
| `CSB1130_001` Jerusalem | verified | William of Tyre, Book XIII, ch. 28, vol. II, pp. 45–46 identifies Jerusalem as the royal residence in the succession narrative. | City point retained. |
| `CSB1130_004` Damascus | verified | Ibn al-Qalanisi/Gibb, AH 524–525, pp. 200–203 names Buri, Damascus, its army, citadel, and palace. | Political-center point retained. |
| `CSB1130_005` Ascalon | unresolved | The recovered modern locators remain too broad for a page-level public claim. | `DISPUTED`; absent from baseline, present only in `inclusive`. |
| `CSB1130_006` Tripoli/Tortosa | partial | William of Tyre, Book XIII, ch. 26, vol. II, pp. 40–42 calls Pons count of Tripoli. The checked pages do not independently establish Tortosa or a continuous county footprint. | `DOWNGRADE`; Tripoli retained, Tortosa deferred to `inclusive`. |
| `CSB1130_008` Antioch | verified | William of Tyre, Book XIII, ch. 27, vol. II, pp. 43–45 records the succession crisis and custody of Antioch. | City point retained. |
| `CSB1130_010` Edessa | partial | William of Tyre, Book XIV, ch. 3, vol. II, p. 51 names Joscelin as count of Edessa in the adjacent 1131 narrative. | `DOWNGRADE`; retained at minor seed weight and never used to claim a perimeter. |
| `CSB1187_001` Cairo/Damascus | partial | Painter, p. 45 styles Saladin sultan of Egypt, Damascus, and Aleppo. It names Damascus, not Cairo, and the title does not define a territory. | `DOWNGRADE`; Damascus retained, Cairo deferred to `inclusive`. |
| `CSB1187_003` Jerusalem | verified | Ibn Shaddad, 1897 edition, ch. 36, pp. 118–120 records surrender and transfer of possession on 2 October 1187. | City point retained. |
| `CSB1187_004` captured coast | partial | Ibn Shaddad, ch. 35, pp. 116–117 supports Acre, Sidon, Beirut, Ascalon, and Gaza. Jaffa is absent from the checked pages. | Supported cities retained; Jaffa marked `DISPUTED` and deferred to `inclusive`. |
| `CSB1187_005` Tyre | verified | Ibn Shaddad, ch. 35, p. 117 and chs. 36–38, pp. 120–122 records the holdout and siege through 30 December. | City point retained for the year-end slice. |
| `CSB1187_007` Tripoli | verified at city level | Ibn Shaddad, ch. 35, p. 114 identifies Tripoli as a refuge after Hattin; Edbury's publisher summary states that Tripoli held out against Saladin. | `KEEP` the city point; no inland county limit inferred. |
| `CSB1187_008` Antioch | verified at city level | Edbury's publisher summary states that Antioch held out against Saladin. | `KEEP` the city point; surrounding lordships remain unresolved. |

After the supplemental review the evidence count is **7 verified, 4 partial, and 1 unresolved**. That count describes the twelve recovered claim groups. It does not erase the seven explicit input decisions below.

## Load-bearing decisions

| Gap | Decision | Baseline treatment |
|---|---|---|
| Jaffa in the 1187 captured-coast group | `DISPUTED` | Omitted; available only in `inclusive`. |
| Ascalon in 1130 | `DISPUTED` | Omitted with the Fatimid entity; available only in `inclusive`. |
| Cairo/Damascus in 1187 | `DOWNGRADE` | Damascus retained as a named political center; Cairo deferred. |
| Antioch at end of 1187 | `KEEP` | City point retained. |
| Edessa through adjacent 1131 material | `DOWNGRADE` | Point retained at minor weight. |
| Tripoli/Tortosa in 1130 | `DOWNGRADE` | Tripoli retained; Tortosa deferred. |
| Tripoli at end of 1187 | `KEEP` | City point retained. |

No reviewed gap was silently filled by a default solver value. No item required `REMOVE`: the unsupported parts already existed as separable seeds and could be deferred without deleting their audit trail.

## Editions and access record

- William of Tyre, *A History of Deeds Done Beyond the Sea*, Babcock/Krey translation (1943), [Internet Archive item `williamoftyrehistory`](https://archive.org/details/williamoftyrehistory), consulted by page; citation-only in the repository.
- Ibn al-Qalanisi, *The Damascus Chronicle of the Crusades*, Gibb translation (1932), [Internet Archive item `the-damascus-chronicle-of-the-crusades`](https://archive.org/details/the-damascus-chronicle-of-the-crusades); the host record carries a Public Domain Mark.
- Baha al-Din Ibn Shaddad, *The Life of Saladin; or, What Befell Sultan Yusuf* (1897), [Internet Archive item `libraryofpalesti13paleuoft`](https://archive.org/details/libraryofpalesti13paleuoft), used as a page-addressable public-domain edition.
- Sidney Painter, “The Third Crusade,” in *A History of the Crusades*, vol. II (1962), p. 45, [JSTOR open-book record](https://www.jstor.org/stable/j.ctv4s7mwv); copyrighted, citation-only.
- Peter W. Edbury, “The Crusader States,” in *The New Cambridge Medieval History*, vol. V (1999), pp. 590–606, [Cambridge publisher record](https://www.cambridge.org/core/books/abs/new-cambridge-medieval-history/crusader-states/35E282BC04D01A0074105E8B1051F233); publisher summary checked, copyrighted, citation-only.
- The Internet Archive item `the-chronicle-of-ibn-al-athir-big-file` was rejected because its uploader, edition metadata, and rights status could not support a public audit trail.

Access date: 2026-09-01. Reference-map access and rights are recorded separately in [`reference-map-register.json`](../../cases/crusader_states/public/reference-map-register.json).

## Geospatial source verification

Natural Earth 1:10m physical vectors, version 5.1.2, supply the land and natural-feature geometry. Comparison with fresh official artifacts found an exact normalized geometry multiset match for 4,133 coastline features and for Jordan River `NE_ID 1159114369`. Mount Lebanon `NE_ID 1730071649` and Taurus `NE_ID 1159103077` were topologically equal with zero symmetric difference after Polygon-to-MultiPolygon type promotion.

Archive URLs and SHA-256 values are recorded in [`natural-earth-source-check.json`](../../cases/crusader_states/public/natural-earth-source-check.json). Approximate locality coordinates cite GeoNames records by `geonameId` under CC BY 4.0.

## Human review boundary

The machine-readable decisions are reproducible, but their scholarly acceptance remains human work. A historian must still judge the 1130 status of Ascalon and Tortosa, the admissibility of the 1131 Edessa bridge, Jaffa in the exact year-end convention, whether Painter's political title is sufficient for a Damascus seed, and how far the surviving cities of Tripoli and Antioch may stand for their surrounding polities. The present project deliberately answers only the locality-level modeling question.
