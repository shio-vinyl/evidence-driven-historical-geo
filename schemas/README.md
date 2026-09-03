# Public Contract Schemas

The v0.2 research loop adds:

- `research-bundle.schema.json` for Source, Observation, Claim, backend-neutral Model Decision, and Evidence Gap records;
- `reconstruction-request.schema.json` for the compiler output consumed by spatial backends;
- `uncertainty-diagnosis.schema.json` for evidence/model scenario attribution;
- `search-targets.schema.json` for spatially justified next-search agendas.

`historical_geo.research_contracts` adds cross-record reference checks and prevents evaluation-only material from entering research claims or model decisions.

The frozen v0.1 compatibility contract remains intentionally small:

- `lineage-bundle.schema.json` defines sources, observations, evidence claims, and reviewed model decisions.
- `solver-input.schema.json` defines the adapter output consumed by XTENT.
- `reconstruction-run.schema.json` defines effective-input and output hashes plus geometry validation state.
- `output-feature.schema.json` defines the lineage and uncertainty properties carried by each boundary hypothesis.

JSON Schema validates structure. `historical_geo.contracts.validate_lineage_bundle` adds referential and semantic checks that JSON Schema alone cannot express, including allocation/display separation, evidence requirements, natural-feature authorization, unknown-coordinate rejection, and bounded ordinal enforcement.
