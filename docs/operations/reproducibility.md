[English](reproducibility.md) | [简体中文](reproducibility.zh-CN.md)

# Reproducibility Guide

## Requirements

- Python 3.9 or newer;
- a wheel-capable package installer;
- enough memory for GeoPandas, Rasterio, scikit-image, and Matplotlib on the clipped fixture.

The repository carries the small public inputs. Reproduction does not require a private project, atlas scan, source PDF, or global GIS dataset.

## Install

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
```

## Validate and run the reviewed baseline

```bash
.venv/bin/historical-geo validate cases/crusader_states/public

MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/public --slice 1130 --scenario reviewed-baseline

MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/public --slice 1187 --scenario reviewed-baseline
```

`run` executes `validate -> build-inputs -> reconstruct -> audit -> render`. Each run writes the effective solver input, boundary-hypothesis GeoJSON, manifest, render QA, and preview below the ignored case `build/` directory.

## Rebuild the scenario set

The declared scenarios are `verified-only`, `reviewed-baseline`, `inclusive`, `flat-natural`, `projection-normal`, `projection-expansive`, `grid-5km`, and `grid-20km`. Run any one with:

```bash
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/public --slice 1130 --scenario verified-only
```

Repeat for both slices and each name above. The 10 km reviewed baseline supplies the common comparison grid. The 5 km and 20 km cases test grid sensitivity without changing historical evidence.

## Regenerate figures and metrics

```bash
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo figures \
  cases/crusader_states/public
```

This command rebuilds all required scenarios for both slices and writes six figures:

- `evidence-anchors.png`;
- `reconstruction-slices.png`;
- `natural-ablation.png` with JSON metrics;
- `boundary-attractor-diagnostics.png` with JSON diagnostics;
- `reference-comparison.png` with categorical comparison JSON;
- `uncertainty-zones.png` with scenario-agreement JSON;
- `figure-qa.json` for nonblank checks and hashes.

The external comparison does not digitize atlas boundaries. The uncertainty classes record agreement within the declared scenario set; they are not probabilities.

## Run tests

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=.cache/matplotlib \
  .venv/bin/pytest -p no:cacheprovider
```

Current expected result: **68 passed**.

## Verify outputs

For every slice and scenario, the audit must report valid geometry, all expected entities retained, and no overlap between entity polygons. The reviewed baseline is written to `build/run-{slice}`; other scenarios use `build/run-{slice}-{scenario}`.

`cases/crusader_states/public/fixture-manifest.json` records byte counts and SHA-256 values for public inputs. `natural-earth-source-check.json` records official Natural Earth artifacts and geometry comparison. Generated run manifests hash the effective inputs and output surfaces.

## Synthetic smoke fixture

```bash
MPLCONFIGDIR=.cache/matplotlib .venv/bin/historical-geo run \
  cases/crusader_states/fixtures/synthetic_smoke --slice 1130
```

This fixture checks software behavior without historical or third-party data. Accepted point seeds and assumption-labeled phases enter allocation; event and route observations stay outside solver inputs.

## Reproducibility boundary

- Generated `build/`, `.cache/`, bytecode, and pytest caches are local artifacts and must remain untracked.
- Exact binary hashes are guaranteed only for the tested dependency stack; geometry validity and semantic QA are the cross-version checks.
- Reproduction tests the recorded agent decision path and model implementation. It does not certify historical truth.
- Reference access may change. The register preserves the consulted URL, access date, rights finding, and the assertions actually recorded.
