import json
from pathlib import Path

from ai_objective_index.mcp_registry_publish_readiness import run_mcp_registry_publish_readiness


def _write(path: str, payload: dict):
    full = Path(path)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(json.dumps(payload), encoding="utf-8")


def test_mcp_registry_publish_readiness_holds_until_pypi_uploaded():
    _write("public_launch/wave2/PYPI_PUBLISH_READINESS_RESULT.json", {"decision": "PASS_BUILD_READY", "dist_files": [{"path": "dist/a.whl"}]})

    result = run_mcp_registry_publish_readiness(pypi_uploaded=False, mcp_publisher_available=True, registry_auth_available=True, write_result=False)

    assert result["decision"] == "HOLD_PYPI_UPLOAD_REQUIRED"
    assert result["submission_performed"] is False


def test_mcp_registry_publish_readiness_metadata_mismatch_blocks(monkeypatch):
    monkeypatch.setattr("ai_objective_index.mcp_registry_publish_readiness._server_json", lambda: {"name": "io.github.bad/name"})

    result = run_mcp_registry_publish_readiness(pypi_uploaded=True, mcp_publisher_available=True, registry_auth_available=True, write_result=False)

    assert result["decision"] == "BLOCK_METADATA_MISMATCH"


def test_mcp_registry_publish_readiness_all_ready_passes():
    _write("public_launch/wave2/PYPI_PUBLISH_READINESS_RESULT.json", {"decision": "PASS_BUILD_READY", "dist_files": [{"path": "dist/a.whl"}]})

    result = run_mcp_registry_publish_readiness(pypi_uploaded=True, mcp_publisher_available=True, registry_auth_available=True, write_result=False)

    assert result["decision"] == "PASS_READY_TO_SUBMIT"
