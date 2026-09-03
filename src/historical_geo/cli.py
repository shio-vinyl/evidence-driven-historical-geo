"""Command line entry point for the public v0.2 research workflow.

The ordinary commands intentionally cross the epistemic-state compiler and the
selected spatial backend.  The frozen v0.1 adapter remains callable only via
``legacy-*`` commands so it can protect the regression baseline without
silently becoming the public execution path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from historical_geo.adapter import _schema_dir, load_case, write_solver_input
from historical_geo.contracts import load_json, validate_lineage_bundle
from historical_geo.pipeline import audit_surface, reconstruct, run_directory
from historical_geo.render import render_surface
from historical_geo.research_case import compile_case_request, reconstruct_research_case, run_research_loop
from historical_geo.research_contracts import (
    load_json as load_research_json,
    validate_research_bundle,
    validate_search_targets,
    validate_uncertainty_diagnosis,
)
from historical_geo.search_policy_experiment import run_policy_experiment_files


def _slice(value: str) -> int | str:
    return int(value) if value.isdigit() else value


def legacy_validate_case(case_dir: Path) -> dict[str, Any]:
    """Validate the frozen v0.1 lineage bundle for regression compatibility."""
    case = load_case(case_dir)
    lineage = load_json(case_dir.resolve() / case["lineage_path"])
    result = validate_lineage_bundle(lineage, _schema_dir() / "lineage-bundle.schema.json")
    return {
        "ok": result.ok,
        "errors": [x.__dict__ for x in result.errors],
        "research_gaps": result.research_gaps,
    }


def validate_case(case_dir: Path) -> dict[str, Any]:
    """Validate the public v0.2 epistemic state used by default commands."""
    case_dir = case_dir.resolve()
    # Also parse the case shell here so relative fixture paths fail before a run.
    load_case(case_dir)
    bundle_path = case_dir / "research-bundle.json"
    if not bundle_path.is_file():
        return {
            "ok": False,
            "errors": [{
                "path": "research-bundle.json",
                "message": "v0.2 research bundle is required; use legacy-validate for a v0.1 fixture",
            }],
        }
    bundle = load_research_json(bundle_path)
    result = validate_research_bundle(bundle)
    errors = [x.__dict__ for x in result.errors]
    rounds = case_dir / "research" / "rounds"
    for path in sorted(rounds.rglob("uncertainty-diagnosis*.json")) if rounds.is_dir() else ():
        artifact = validate_uncertainty_diagnosis(load_research_json(path), bundle)
        errors.extend(
            {**issue.__dict__, "path": f"{path.relative_to(case_dir)}:{issue.path}"}
            for issue in artifact.errors
        )
    for path in sorted(rounds.rglob("search-targets*.json")) if rounds.is_dir() else ():
        artifact = validate_search_targets(load_research_json(path), bundle)
        errors.extend(
            {**issue.__dict__, "path": f"{path.relative_to(case_dir)}:{issue.path}"}
            for issue in artifact.errors
        )
    if not errors:
        scenario_manifest = load_research_json(case_dir / "research-scenarios.json")
        slices = sorted(
            {
                decision.get("parameters", {}).get("slice")
                for decision in bundle.get("model_decisions", [])
                if "slice" in decision.get("parameters", {})
            },
            key=lambda value: (type(value).__name__, str(value)),
        )
        for scenario in sorted(scenario_manifest.get("scenarios", {})):
            for slice_value in slices:
                try:
                    compile_case_request(case_dir, slice_value, scenario)
                except ValueError as exc:
                    errors.append({
                        "code": "invalid_scenario",
                        "path": f"research-scenarios.json:{scenario}:{slice_value}",
                        "message": str(exc),
                    })
    return {
        "ok": not errors,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="historical-geo")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (
        "validate", "validate-research", "compile-request", "reconstruct", "research-run", "audit", "render", "run", "figures",
        "research-loop", "legacy-validate", "legacy-build-inputs", "legacy-reconstruct", "legacy-run",
    ):
        command = sub.add_parser(name)
        command.add_argument("case", type=Path)
        if name not in {"validate", "validate-research", "legacy-validate", "figures"}:
            command.add_argument("--slice", required=True, type=_slice)
        if name in {
            "compile-request", "reconstruct", "research-run", "audit", "render", "run",
            "legacy-build-inputs", "legacy-reconstruct", "legacy-run",
        }:
            command.add_argument("--scenario", default="reviewed-baseline")
    experiment = sub.add_parser("policy-experiment")
    experiment.add_argument("experiment", type=Path)
    experiment.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "policy-experiment":
        result = run_policy_experiment_files(args.experiment.resolve(), args.output)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    case_dir = args.case.resolve()

    if args.command == "figures":
        from historical_geo.figures import build_case_figures

        print(build_case_figures(case_dir))
        return 0
    if args.command in {"validate", "validate-research"}:
        result = validate_case(case_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1
    if args.command == "legacy-validate":
        result = legacy_validate_case(case_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1
    if args.command == "compile-request":
        print(json.dumps(compile_case_request(case_dir, args.slice, args.scenario), indent=2, sort_keys=True))
        return 0
    if args.command == "research-run":
        print(reconstruct_research_case(case_dir, args.slice, args.scenario))
        return 0
    if args.command == "research-loop":
        diagnosis, targets = run_research_loop(case_dir, args.slice)
        print(json.dumps({"diagnosis": str(diagnosis), "search_targets": str(targets)}, indent=2, sort_keys=True))
        return 0
    if args.command == "legacy-build-inputs":
        print(write_solver_input(case_dir, args.slice, scenario=args.scenario))
        return 0
    if args.command == "legacy-reconstruct":
        print(reconstruct(case_dir, args.slice, scenario=args.scenario))
        return 0
    if args.command == "reconstruct":
        print(reconstruct_research_case(case_dir, args.slice, args.scenario))
        return 0
    run_dir = run_directory(case_dir, args.slice, args.scenario)
    if args.command == "audit":
        effective = load_json(run_dir / "effective-solver-input.json")
        expected = sorted({x["parameters"]["entity"] for x in effective["phases"]})
        result = audit_surface(run_dir / "boundary-hypotheses.geojson", expected_entities=expected)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if all(result.values()) else 1
    if args.command == "render":
        print(render_surface(run_dir))
        return 0
    if args.command == "legacy-run":
        validation = legacy_validate_case(case_dir)
        if not validation["ok"]:
            print(json.dumps(validation, indent=2, sort_keys=True))
            return 1
        write_solver_input(case_dir, args.slice, scenario=args.scenario)
        run_dir = reconstruct(case_dir, args.slice, scenario=args.scenario)
        render_surface(run_dir)
        print(run_dir)
        return 0

    validation = validate_case(case_dir)
    if not validation["ok"]:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 1
    run_dir = reconstruct_research_case(case_dir, args.slice, scenario=args.scenario)
    render_surface(run_dir)
    print(run_dir)
    return 0
