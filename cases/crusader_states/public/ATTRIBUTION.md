# Fixture attribution and rights

## Redistributed geometry

The clipped land mask, mountain-region polygons, and Jordan River centerline are derived from **Natural Earth 1:10m physical vectors, version 5.1.2**. Natural Earth places its data in the public domain: <https://www.naturalearthdata.com/about/terms-of-use/>.

The curated input was compared with fresh official 5.1.2 archives on 2026-09-01. The coastline geometry multiset matched exactly (4,133 features); Jordan River feature `NE_ID 1159114369` matched exactly; Mount Lebanon `NE_ID 1730071649` and Taurus `NE_ID 1159103077` were topologically equal with zero symmetric difference, with only Polygon-to-MultiPolygon type promotion in the curated GeoPackage. Official URLs, archive SHA-256 values, and comparison hashes are recorded in `natural-earth-source-check.json`.

## Gazetteer coordinates

Settlement locality points cite **GeoNames** records by `geonameId`. GeoNames publishes its data under Creative Commons Attribution 4.0: <https://www.geonames.org/export/>. Coordinates are labeled `approximate`; they are not claims about exact historical settlement footprints.

## Historical sources

Books and articles in `lineage.json` are `citation_only`. This fixture redistributes no scans, source text, or copyrighted map imagery. Claim strings are project paraphrases linked to bibliographic locators. Exact page checks, input decisions, and remaining scholarly questions are recorded in `docs/research/source-review.md` and `historical-claim-decisions.json`.

## Reference maps

`reference-map-register.json` records author, edition, date alignment, prior exposure, access, and rights for each comparator. The Andrew Buck 1130 map is copyrighted and was unavailable in the legal preview; no assertion or geometry was extracted. The Shepherd and Johnston/Poole images carry public-domain records on Wikimedia Commons, but their scans and traced boundaries are intentionally absent from this repository.

`figures/reference-comparison.png` is an original categorical summary built from hand-recorded city, entity, adjacency, and coastal-sequence observations. It is not a reproduction of any atlas plate.
