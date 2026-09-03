[English](source-review.md) | [简体中文](source-review.zh-CN.md)

# Historical Source Review

## Review method

The research agent searches catalogues, legal repositories, publisher records, and page-addressable editions; records access and rights; writes a narrow paraphrase; and then decides whether the resulting claim may constrain the solver. A bibliographic citation without a checked locator does not meet the public-case threshold. Conflicting, incomplete, or rejected material remains visible in lineage.

The review unit is deliberately local. A control statement can support a locality seed. A title or campaign event may supply context, but cannot establish a territorial perimeter. A gazetteer coordinate locates the modern approximation of a named place; it does not reproduce a medieval settlement footprint.

Round 01 followed the spatial diagnosis without consulting held-out historical boundary maps. Its check selection, locators, outcomes, and limitations are preserved in [`source-checks.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/source-checks.json).

## Current machine-readable state

The current [`research-bundle.json`](../../cases/crusader_states/public/research-bundle.json) contains 23 sources, 63 observations, 23 claims, 33 model decisions, and nine evidence gaps. Twenty-one claims are `supported` and two are `unresolved`. Restricting the count to locality claims gives 18 supported localities and two unresolved localities: Ascalon and Tortosa in 1130.

There are 20 control-point decisions: 18 `admitted` and two `experimental`. The two experimental decisions are the 1130 Ascalon and Tortosa seeds. Four of nine evidence gaps are closed; five remain open.

The frozen round-00 [`research-bundle.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-bundle.snapshot.json) and [`research-scenarios.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-scenarios.snapshot.json) reproduce the reviewed v0.1 inputs. The legacy [`historical-claim-decisions.json`](../../cases/crusader_states/public/historical-claim-decisions.json) records that initial review pass. Round-01 transitions superseding its Cairo, Jaffa, Edessa, and Tripoli wording are explicitly recorded in [`state-changes.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/state-changes.json). The research bundle and state-change record are authoritative for the current epistemic state.

## Claim-level result

| Locality or group | Current result | Checked basis and limit | Current solver consequence |
|---|---|---|---|
| Jerusalem, 1130 | supported | William of Tyre, Book XIII, ch. 28, vol. II, pp. 45–46 identifies Jerusalem as the royal residence in the succession narrative. | City point admitted. |
| Damascus, 1130 | supported | Ibn al-Qalanisi/Gibb, AH 524–525, pp. 200–203 names Buri, Damascus, its army, citadel, and palace. | Political-center point admitted. |
| Ascalon, 1130 | unresolved | The recovered modern locators remain too broad for a page-level public claim. | Experimental; absent from baseline and available only in `inclusive`. |
| Tripoli and Tortosa, 1130 | mixed | William of Tyre, Book XIII, ch. 26, vol. II, pp. 40–42 supports Tripoli as the comital center. The checked material still does not independently establish Tortosa for the slice. | Tripoli admitted; Tortosa remains experimental and `inclusive`-only. |
| Rafaniyya, 1130 | supported | Lewis, pp. 100–102 and 139, bounds comital possession from 1126 to permanent loss in 1137. Syriaca.org place 496 supplies an approximate coordinate. | New minor control point admitted; no continuous county footprint inferred. |
| Antioch, 1130 | supported | William of Tyre, Book XIII, ch. 27, vol. II, pp. 43–45 records the succession crisis and custody of Antioch. | City point admitted. |
| Edessa, 1130 | supported | Asbridge, pp. 125–126, treats Joscelin's leadership through the section's 1130 endpoint; William of Tyre, Book XIV, ch. 3, vol. II, p. 51 supplies adjacent-1131 corroboration. | Temporal gap closed; point remains admitted at minor weight. |
| Cairo, 1187 | supported at operational-locality level | Lane-Poole, p. 219, names al-Adil marching from Cairo. Ibn Shaddad, pp. 104–105 and 108, supplies Egyptian administrative and military context without naming Cairo in those passages. | Cairo admitted as an operational point; it does not proxy all Egypt. |
| Damascus, 1187 | supported at political-center level | Painter, p. 45, styles Saladin sultan of Egypt, Damascus, and Aleppo. | Damascus point admitted; the title does not define extent. |
| Jerusalem, 1187 | supported | Ibn Shaddad, 1897 edition, ch. 36, pp. 118–120 records surrender and transfer of possession on 2 October 1187. | City point admitted. |
| Acre, Sidon, Beirut, Ascalon, and Gaza, 1187 | supported | Ibn Shaddad, ch. 35, pp. 116–117 and associated checked observations support their capture or surrender. | Locality points admitted; no coastal polygon inferred. |
| Jaffa, 1187 | supported at locality level | Lane-Poole, p. 219, states that al-Adil took Jaffa by assault. Kauffeldt, p. 78 and n. 225, reproduces a contemporary letter through a citation to Edbury 2007, pp. 160–162. | Jaffa admitted; the mediated transmission remains a stated limitation, and its isolated grid effect is zero. |
| Tyre, 1187 | supported | Ibn Shaddad, ch. 35, p. 117 and chs. 36–38, pp. 120–122 records the holdout and siege through 30 December. | City point admitted for the year-end slice. |
| Tripoli, 1187 | supported at city level | Ibn Shaddad, ch. 35, p. 114 identifies Tripoli as a refuge after Hattin; Edbury's publisher summary states that Tripoli held out. | City point admitted; inland extent is not inferred. |
| Antioch, 1187 | supported at city level | Edbury's publisher summary states that Antioch held out against Saladin. | City point admitted; surrounding lordships remain unmodeled as evidence. |

“Supported” means that the stored, narrowly worded claim meets this project's review threshold. It does not mean that the source is uncontested or that a historian has accepted the resulting solver decision.

## Round-01 source additions and checks

- Thomas S. Asbridge, *The Creation of the Principality of Antioch, 1098–1130* (2000), pp. 125–126, [official Google Books record](https://books.google.com/books/about/The_Creation_of_the_Principality_of_Anti.html?id=DvUNedDOoFgC). Copyrighted and citation-only; the preview may not expose the cited pages in every region.
- Baha al-Din Ibn Shaddad, *The Life of Saladin; or, What Befell Sultan Yusuf* (1897), pp. 104–105 and 108, [Internet Archive record](https://archive.org/details/lifesaladin00condgoog). A page-addressable public-domain edition; these passages support Egyptian context but do not name Cairo.
- Stanley Lane-Poole, *Saladin and the Fall of the Kingdom of Jerusalem* (1898), p. 219, [public-domain scan](https://upload.wikimedia.org/wikipedia/commons/3/3e/Saladin_and_the_fall_of_the_Kingdom_of_Jerusalem_%28IA_saladinfallofkin00lane%29.pdf). A secondary synthesis that cites Ibn al-Athir.
- Sebastian Fons Kauffeldt, master's thesis (Roskilde University, 2019), p. 78 and n. 225, [open repository PDF](https://rucforsk.ruc.dk/ws/files/63773770/Speciale_Sebastian_Kauffeldt_Jerusalem_1099_1187.pdf). It mediates the contemporary letter through Edbury 2007; the repository retains only a citation.
- Kevin James Lewis, *The Counts of Tripoli and Lebanon in the Twelfth Century* (2017), pp. 100–102 and 139, [digital copy](https://api.nla.am/server/api/core/bitstreams/bbc0405c-0d70-411b-ae3e-623e3457c101/content). Copyrighted and citation-only.
- Syriaca.org, *The Syriac Gazetteer*, [Rafaniyya, place 496](https://syriaca.org/place/496). Used only for an attributed approximate location.

The round was accessed on 2026-09-03. Earlier editions and access decisions remain recorded on their source objects in the research bundle. The repository contains no source scan, atlas page, long quotation, or copyrighted book text.

## Current gap decisions

| Question | Machine status | Human review still required |
|---|---|---|
| Ascalon in 1130 | open; seed `experimental` | Decide whether directly locatable evidence supports Fatimid control at the exact slice. |
| Tortosa in 1130 | open; seed `experimental` | Decide whether a checked source independently establishes locality control near 1130. |
| Edessa in 1130 | closed; seed `admitted` at minor weight | Accept or reject Asbridge's temporal coverage and the adjacent-year corroboration. |
| Cairo in 1187 | closed; seed `admitted` | Accept or reject the operational-point inference from Lane-Poole plus Ibn Shaddad's context. |
| Jaffa in 1187 | closed; seed `admitted` | Accept or reject the locality inference from a secondary account and a mediated contemporary letter. |
| Tripoli inland evidence in 1130 | closed; Rafaniyya seed `admitted` at minor weight | Accept or reject the dated-possession reading and approximate gazetteer location; no county perimeter follows. |
| Surviving Latin extent in 1187 | open | Identify additional year-end localities, routes, or explicit exclusions around Tyre, Tripoli, and Antioch. |
| Reach assumptions in both slices | two open model gaps | Diagnose or replace the current backend assumptions; source search alone cannot close them. |

## Geospatial source verification

Natural Earth 1:10m physical vectors, version 5.1.2, supply land and natural-feature geometry. Approximate locality coordinates cite their gazetteers; GeoNames data is attributed under CC BY 4.0, and the new Rafaniyya point cites Syriaca.org directly. Archive URLs and SHA-256 values for Natural Earth inputs are recorded in [`natural-earth-source-check.json`](../../cases/crusader_states/public/natural-earth-source-check.json).

## Human review boundary

The machine records reproduce why each input entered, remained experimental, or was excluded. Scholarly acceptance remains human work. In particular, closing Cairo, Jaffa, Edessa, and Rafaniyya gaps records that the project's declared success criteria were met. It does not transform those decisions into settled historical facts, and no locality claim authorizes a recovered territorial boundary by itself.
