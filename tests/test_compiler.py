from __future__ import annotations

import ast
from copy import deepcopy
import inspect

import pytest

from historical_geo.compiler import compile_reconstruction_request, reconstruction_request_bytes


def research_bundle() -> dict:
    return {
        "contract_version": "historical_geo.research_bundle.v0.2",
        "case_id": "compiler-test",
        "sources": [{
            "source_id": "SRC", "title": "Reviewed source", "source_type": "book",
            "rights_status": "citation permitted", "redistribution": "citation_only", "use_role": "research",
        }],
        "observations": [{
            "observation_id": "OBS", "source_id": "SRC", "locator": "p. 1",
            "paraphrase": "A control point.", "verification_status": "reviewed",
        }],
        "claims": [{
            "claim_id": "CLM", "supporting_observation_ids": ["OBS"],
            "challenging_observation_ids": [], "semantic_role": "control_point",
            "status": "supported", "rationale": "Direct source statement.",
            "statement": "Control is attested.", "entity": "Polity", "slice": 1130,
        }],
        "model_decisions": [
            {
                "decision_id": "DEC_ADMITTED", "role": "control_point", "review_status": "admitted",
                "supporting_claim_ids": ["CLM"], "challenging_claim_ids": [], "source_ids": ["SRC"],
                "rationale": "A point input.",
                "parameters": {"slice": 1130, "entity": "Polity", "name": "City", "coordinates": [35, 31], "weight_class": "major"},
            },
            {
                "decision_id": "DEC_EXPERIMENT", "role": "spatial_constraint", "review_status": "experimental",
                "supporting_claim_ids": ["CLM"], "challenging_claim_ids": [], "source_ids": ["SRC"],
                "rationale": "Test an extent prior.",
                "parameters": {"slice": 1130, "constraint_kind": "extent_prior", "entity": "Polity", "reach_class": "normal"},
            },
            {
                "decision_id": "DEC_EXCLUDED", "role": "display_context", "review_status": "excluded",
                "supporting_claim_ids": ["CLM"], "challenging_claim_ids": [], "source_ids": ["SRC"],
                "rationale": "Do not reconstruct from display context.", "parameters": {"slice": 1130},
            },
            {
                "decision_id": "DEC_ASSUMPTION", "role": "traversal_constraint", "review_status": "assumption",
                "supporting_claim_ids": [], "challenging_claim_ids": [], "source_ids": [],
                "rationale": "A declared friction assumption.", "assumption_reason": "Required for the test.",
                "parameters": {"slice": 1130, "constraint_kind": "friction_feature", "feature_id": "ridge", "strength": "soft"},
            },
        ],
        "evidence_gaps": [],
    }


def test_compiler_keeps_only_generic_inputs_and_enforces_scenario_activation() -> None:
    bundle = research_bundle()
    baseline = compile_reconstruction_request(bundle, 1130, {"name": "baseline", "axis": "baseline"}, {"resolution": 1})
    assert {item["decision_id"] for item in baseline["inputs"]} == {"DEC_ADMITTED", "DEC_ASSUMPTION"}
    assert "seeds" not in baseline and "phases" not in baseline and "barriers" not in baseline

    evidence = compile_reconstruction_request(
        bundle, 1130,
        {"name": "with-experiment", "axis": "evidence", "included_decision_ids": ["DEC_EXPERIMENT", "DEC_EXCLUDED"]},
        {"resolution": 1},
    )
    assert {item["decision_id"] for item in evidence["inputs"]} == {"DEC_ADMITTED", "DEC_ASSUMPTION", "DEC_EXPERIMENT"}
    experiment = next(item for item in evidence["inputs"] if item["decision_id"] == "DEC_EXPERIMENT")
    assert experiment["claim_ids"] == ["CLM"]
    assert experiment["source_ids"] == ["SRC"]


def test_compiler_output_is_byte_deterministic() -> None:
    first = compile_reconstruction_request(
        research_bundle(), 1130, {"name": "baseline", "axis": "baseline"}, {"resolution": 1, "bbox": [0, 0, 1, 1]}
    )
    reordered = research_bundle()
    reordered["model_decisions"].reverse()
    second = compile_reconstruction_request(
        reordered, 1130, {"axis": "baseline", "name": "baseline"}, {"bbox": [0, 0, 1, 1], "resolution": 1}
    )
    assert reconstruction_request_bytes(first) == reconstruction_request_bytes(second)
    assert [item["decision_id"] for item in first["inputs"]] == sorted(item["decision_id"] for item in first["inputs"])


def test_compiler_requires_explicit_profile_name_and_axis() -> None:
    with pytest.raises(ValueError, match="name"):
        compile_reconstruction_request(research_bundle(), 1130, {"axis": "baseline"}, {})
    with pytest.raises(ValueError, match="axis"):
        compile_reconstruction_request(research_bundle(), 1130, {"name": "bad", "axis": "experimental"}, {})


def test_generic_compiler_has_no_solver_or_pipeline_import() -> None:
    import historical_geo.compiler as compiler

    imports = []
    for node in ast.walk(ast.parse(inspect.getsource(compiler))):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    assert not any(name == "historical_geo.xtent" or name == "historical_geo.pipeline" for name in imports)
