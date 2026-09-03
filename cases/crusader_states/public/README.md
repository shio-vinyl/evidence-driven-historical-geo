# Public Crusader States case fixture

This fixture is the first worked testbed for an auditable spatial research agent. A research agent can inspect sources, preserve observations and claims, make explicit backend-neutral decisions, run controlled evidence and model scenarios, diagnose consequential uncertainty, and derive the next evidence-search agenda.

It regenerates **1130** and **end-of-year 1187** from paraphrased claims, bibliographic citations, approximate gazetteer points, and clipped physical vectors. `research-bundle.json` stores the v0.2 epistemic state. `research-scenarios.json` defines the evidence/model interventions. `research/rounds/00-initial/` records the resulting diagnosis and ranked search targets. `baseline-manifest.json` freezes the earlier v0.1 behavior for regression checks.

## Interpretation boundary

- City control, political centers, events, routes, and territorial extent are distinct evidence roles.
- GeoNames coordinates are approximate locality points.
- XTENT projection classes and natural-friction ordinals are declared model assumptions.
- Mount Lebanon and Taurus supply sensitivity-test geometry. The Jordan River is display context and a rejected boundary-attractor candidate.
- Every polygon is a **boundary hypothesis**, not evidence of an observed historical border.
- Reviewed seed cells are retained when another center has greater modeled influence; this protects point evidence without turning a weak point into a broad claim.
- External maps are comparators, never ground truth, and they do not tune model parameters.
- Scenario agreement is a stability diagnostic, not a probability surface.
- The external maps are evaluation-only. This case remains retrospective because those maps were inspected during development; it is not claimed as a strict blind benchmark.

## Reproduce

From the repository root:

```bash
PYTHONPATH=src python3 -m historical_geo validate cases/crusader_states/public
PYTHONPATH=src python3 -m historical_geo compile-request cases/crusader_states/public \
  --slice 1130 --scenario reviewed-baseline
PYTHONPATH=src python3 -m historical_geo run cases/crusader_states/public --slice 1130
PYTHONPATH=src python3 -m historical_geo research-loop cases/crusader_states/public --slice 1130
PYTHONPATH=src python3 -m historical_geo research-loop cases/crusader_states/public --slice 1187
PYTHONPATH=src python3 -m historical_geo figures cases/crusader_states/public
```

`validate`, `compile-request`, and `run` pass through the v0.2 research compiler and the XTENT backend. The frozen v0.1 adapter is reserved for explicit `legacy-*` compatibility commands. The figure command rebuilds the evidence, natural-cost, projection, and grid scenarios needed for comparison. Build intermediates remain in the ignored `build/` directory. Reviewed figures and machine-readable QA are in `figures/`.

`research/experiments/equal-budget-policy/` is a constructed deterministic replay of targeted, fixed, and broad search orders. It uses declared fixture outcomes to check equal-budget selection and accounting only; it does not evaluate real search effectiveness.

See `ATTRIBUTION.md`, `fixture-manifest.json`, and `figures/README.md` for rights, integrity, and interpretation details.
