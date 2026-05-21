import json
from pathlib import Path

from ai_objective_index.version_apply_gate import run_version_apply_gate


def _fixture(root: Path) -> None:
    (root / ".mcp").mkdir(parents=True)
    (root / "src" / "ai_objective_index").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        '[project]\nname = "ai-objective-index"\nversion = "0.2.0"\n',
        encoding="utf-8",
    )
    (root / ".mcp" / "server.json").write_text(
        json.dumps(
            {
                "name": "io.github.Isometric-Architect/ai-objective-index",
                "version": "0.2.0",
                "packages": [{"identifier": "ai-objective-index", "version": "0.2.0"}],
            }
        ),
        encoding="utf-8",
    )
    (root / "src" / "ai_objective_index" / "__init__.py").write_text('__version__ = "0.2.0"\n', encoding="utf-8")


def test_version_apply_gate_dry_run_does_not_modify(tmp_path):
    _fixture(tmp_path)
    before = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    result = run_version_apply_gate(root=tmp_path, write_result=False)

    assert result["dry_run"] is True
    assert result["version_changed"] is False
    assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == before
    assert result["token_printed"] is False


def test_version_apply_gate_updates_versions(tmp_path):
    _fixture(tmp_path)
    result = run_version_apply_gate(apply_version="0.3.0a1", root=tmp_path, write_result=False)
    server = json.loads((tmp_path / ".mcp" / "server.json").read_text(encoding="utf-8"))

    assert result["version_changed"] is True
    assert result["new_pyproject_version"] == "0.3.0a1"
    assert server["version"] == "0.3.0a1"
    assert server["packages"][0]["version"] == "0.3.0a1"
    assert '__version__ = "0.3.0a1"' in (tmp_path / "src" / "ai_objective_index" / "__init__.py").read_text(encoding="utf-8")


def test_version_apply_gate_rejects_invalid_version(tmp_path):
    _fixture(tmp_path)
    result = run_version_apply_gate(apply_version="not a version", root=tmp_path, write_result=False)

    assert result["errors"]
    assert result["version_changed"] is False
