from __future__ import annotations

from pathlib import Path
import re

import historical_geo


ROOT = Path(__file__).resolve().parents[1]


def _public_files() -> list[Path]:
    ignored = {".git", ".venv", ".cache", ".pytest_cache", "__pycache__", "build"}
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not ignored.intersection(path.relative_to(ROOT).parts)
    ]


def test_release_has_no_ops_tree_and_ignores_generated_caches() -> None:
    assert not (ROOT / ".ops").exists()
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".pytest_cache/" in ignore
    assert "__pycache__/" in ignore
    assert "*.py[cod]" in ignore
    assert "*.egg-info/" in ignore
    assert "dist/" in ignore
    assert "build/" in ignore
    assert "*.whl" in ignore


def test_release_declares_code_and_data_terms() -> None:
    assert "MIT License" in (ROOT / "LICENSE").read_text(encoding="utf-8")
    terms = (ROOT / "DATA-LICENSE.md").read_text(encoding="utf-8")
    assert "Natural Earth" in terms
    assert "GeoNames" in terms
    assert "Creative Commons Attribution 4.0" in terms


def test_release_version_is_stable_and_consistent() -> None:
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', project, re.MULTILINE)
    assert match is not None
    assert match.group(1) == historical_geo.__version__ == "0.3.0"


def test_packaged_schemas_match_public_contract_files() -> None:
    public = ROOT / "schemas"
    packaged = ROOT / "src/historical_geo/schemas"
    assert {path.name for path in packaged.glob("*.json")} == {
        path.name for path in public.glob("*.json")
    }
    for path in public.glob("*.json"):
        assert path.read_bytes() == (packaged / path.name).read_bytes()


def test_release_workflow_runs_supported_python_test_matrix() -> None:
    workflow = (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    assert 'python-version: ["3.9", "3.11"]' in workflow
    assert "python -m pip install -e '.[test]'" in workflow
    assert "python -m pytest -p no:cacheprovider" in workflow
    assert "python -m pip wheel --no-deps" in workflow
    assert 'historical-geo validate "$GITHUB_WORKSPACE/cases/crusader_states/public"' in workflow
    assert 'historical-geo validate "$GITHUB_WORKSPACE/cases/mercia_welsh_frontier/public"' in workflow
    assert 'historical-geo validate "$GITHUB_WORKSPACE/cases/sennacherib_701_southern_levant/public"' in workflow


def test_agent_guide_has_no_ops_maintenance_system() -> None:
    guide = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert ".ops" not in guide


def test_public_text_has_no_local_machine_paths() -> None:
    markers = ("/" + "Users/", "/private/" + "tmp/", "historical-geo-" + "final")
    offenders = []
    for path in _public_files():
        if path.suffix.lower() not in {".md", ".json", ".py", ".toml", ".yml", ".yaml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in markers):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_local_markdown_links_resolve() -> None:
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    missing = []
    for document in sorted(ROOT.rglob("*.md")):
        if ".git" in document.parts:
            continue
        for target in pattern.findall(document.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")) or target.startswith("#"):
                continue
            path_text = target.split("#", 1)[0]
            if path_text and not (document.parent / path_text).resolve().exists():
                missing.append(f"{document.relative_to(ROOT)} -> {target}")
    assert missing == []
