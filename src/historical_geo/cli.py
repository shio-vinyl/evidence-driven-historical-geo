"""Command line entry point for the minimum public recovery path."""

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
from historical_geo.research_contracts import load_json as load_research_json, validate_research_bundle


def _slice(value: str) -> int | str:
    return int(value) if value.isdigit() else value


def validate_case(case_dir: Path) -> dict[str, Any]:
    case = load_case(case_dir)
    lineage = load_json(case_dir.resolve() / case["lineage_path"])
    result = validate_lineage_bundle(lineage, _schema_dir() / "lineage-bundle.schema.json")
    return {
        "ok": result.ok,
        "errors": [x.__dict__ for x in result.errors],
        "research_gaps": result.research_gaps,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="historical-geo")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (
        "validate", "validate-research", "compile-request", "research-run", "research-loop",
        "build-inputs", "reconstruct", "audit", "render", "run", "figures",
    ):
        command = sub.add_parser(name)
        command.add_argument("case", type=Path)
        if name not in {"validate", "validate-research", "figures"}:
            command.add_argument("--slice", required=True, type=_slice)
        if name in {"compile-request", "research-run", "build-inputs", "reconstruct", "audit", "render", "run"}:
            command.add_argument("--scenario", default="reviewed-baseline")
    args = parser.parse_args(argv)
    case_dir = args.case.resolve()

    if args.command == "figures":
        from historical_geo.figures import build_case_figures

        print(build_case_figures(case_dir))
        return 0
    if args.command == "validate":
        result = validate_case(case_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1
    if args.command == "validate-research":
        result = validate_research_bundle(load_research_json(case_dir / "research-bundle.json"))
        print(json.dumps({"ok": result.ok, "errors": [x.__dict__ for x in result.errors]}, indent=2, sort_keys=True))
        return 0 if result.ok else 1
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
    if args.command == "build-inputs":
        print(write_solver_input(case_dir, args.slice, scenario=args.scenario))
        return 0
    if args.command == "reconstruct":
        print(reconstruct(case_dir, args.slice, scenario=args.scenario))
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
    validation = validate_case(case_dir)
    if not validation["ok"]:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 1
    write_solver_input(case_dir, args.slice, scenario=args.scenario)
    run_dir = reconstruct(case_dir, args.slice, scenario=args.scenario)
    render_surface(run_dir)
    print(run_dir)
    return 0
