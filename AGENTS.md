# Agent Guide

This directory is a clean staging repository for a future public GitHub release.

## Read Order

1. `README.md`
2. `.ops/roadmap.md`
3. the active plan and relevant task
4. only the documentation required by that task

## Source Preservation

- Treat the external compiler worktree supplied by the active recovery task as read-only unless the task explicitly says otherwise.
- Treat the external publisher archive supplied by the active recovery task as an immutable snapshot.
- Treat external atlas/vectorization material as private research material by default.
- Keep external machine paths in the task context, never in public repository files.
- Copy only files listed in the recovery manifest; do not bulk-copy an old project or generated-output tree.
- Record the origin and transformation of recovered code, data, and documentation.

## Public Claims

- Call model outputs `boundary hypotheses`, `territorial surfaces`, or `reconstructions`, not true historical borders.
- Keep observations, evidence claims, model decisions, solver inputs, and display-only annotations distinct.
- A natural feature may affect allocation or boundary alignment only when its historical role is supported or explicitly marked as a modeling assumption.
- Defaults and calibration values must never be presented as source evidence.

## Public-Safety Rules

- Do not add source PDFs, book scans, copyrighted atlas pages, large raw datasets, secrets, local settings, caches, or absolute machine paths.
- Prefer clipped, redistributable fixtures with explicit attribution and licenses.
- Public-facing narrative documentation is maintained in paired English and Simplified Chinese versions. `README.md` is the English landing page, `README.zh-CN.md` is its Chinese pair, and documents use the `.zh-CN.md` suffix. Keep paired documents structurally aligned. Internal `.ops` documents may use either language.

## Project Operations

- `.ops/tasks/**` is the execution source.
- `docs/` contains the paired public methodology, case-study, source-review, and reproducibility series; development history stays under the ignored `.ops/` tree.
- Stop before publishing, pushing, choosing a license for third-party material, or declaring a historical result validated without human review.
