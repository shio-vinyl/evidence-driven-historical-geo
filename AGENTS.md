# Agent Guide

This directory is a public-facing research software repository.

## Read Order

1. `README.md`
2. `docs/architecture/methodology.md`
3. the relevant case README and machine-readable research round

## Evidence and Data Preservation

- Treat external atlas/vectorization material as private research material by default.
- Keep external machine paths in task context, never in public repository files.
- Record the origin, rights status, and transformation of incorporated code, data, and documentation.
- Do not replace frozen research-round inputs; add a new reviewed round when epistemic state changes.

## Public Claims

- Call model outputs `boundary hypotheses`, `territorial surfaces`, or `reconstructions`, not true historical borders.
- Keep observations, evidence claims, model decisions, solver inputs, and display-only annotations distinct.
- A natural feature may affect allocation or boundary alignment only when its historical role is supported or explicitly marked as a modeling assumption.
- Defaults and calibration values must never be presented as source evidence.

## Public-Safety Rules

- Do not add source PDFs, book scans, copyrighted atlas pages, large raw datasets, secrets, local settings, caches, or absolute machine paths.
- Prefer clipped, redistributable fixtures with explicit attribution and licenses.
- Public-facing narrative documentation is maintained in paired English and Simplified Chinese versions. `README.md` is the English landing page, `README.zh-CN.md` is its Chinese pair, and documents use the `.zh-CN.md` suffix. Keep paired documents structurally aligned.

## Repository maintenance

- Keep execution state in code, tests, case artifacts, and concise public documentation.
- `docs/` contains the paired public methodology, case-study, source-review, and reproducibility series.
- The MIT license covers original software and documentation. Preserve the separate third-party terms and attribution in `DATA-LICENSE.md` and case attribution records.
- Stop before pushing or declaring a historical result validated without human review unless the user explicitly authorizes it.
