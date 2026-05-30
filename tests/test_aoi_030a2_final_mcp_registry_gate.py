from pathlib import Path

from ai_objective_index import aoi_030a2_final_mcp_registry_gate as gate
from ai_objective_index.aoi_030a2_marker_sync import CANONICAL_MCP_NAME, MCP_MARKER, PACKAGE_NAME, TARGET_VERSION


def _state():
    return {
        "server_package_registry_type": "pypi",
        "server_package_identifier": PACKAGE_NAME,
        "server_package_version": TARGET_VERSION,
    }


def _json(path: Path):
    if str(path).replace("\\", "/").endswith(".mcp/server.json"):
        return {"name": CANONICAL_MCP_NAME, "version": TARGET_VERSION}
    return {}


def _patch_good(monkeypatch):
    monkeypatch.setattr(gate, "_read_or_run_preflight", lambda: {"decision": "PASS_READY_FOR_FINAL_PYPI_UPLOAD"})
    monkeypatch.setattr(gate, "current_marker_state", _state)
    monkeypatch.setattr(gate, "read_json", _json)
    monkeypatch.setattr(gate, "read_text", lambda path: MCP_MARKER)


def test_mcp_registry_gate_requires_pypi_verify(monkeypatch):
    _patch_good(monkeypatch)

    result = gate.run_final_mcp_registry_gate(
        pypi_verify_result={"decision": "HOLD_PYPI_UPLOAD_NOT_CONFIRMED"},
        publisher_finder=lambda: "mcp-publisher",
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "HOLD_PYPI_VERIFY_REQUIRED"


def test_mcp_registry_gate_env_required_after_validate(monkeypatch):
    _patch_good(monkeypatch)

    result = gate.run_final_mcp_registry_gate(
        env={},
        pypi_verify_result={"decision": "PASS_REAL_PYPI_INSTALL_030A2"},
        runner=lambda command, timeout=120: {"ok": True, "returncode": 0, "stdout": "valid", "stderr": ""},
        publisher_finder=lambda: "mcp-publisher",
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "PASS_READY_FOR_MCP_REGISTRY_PUBLISH_ENV_REQUIRED"


def test_mcp_registry_publish_requires_env():
    from ai_objective_index import aoi_030a2_final_mcp_registry_publish as publish

    result = publish.run_final_mcp_registry_publish(
        execute=True,
        env={},
        gate_result={"decision": "PASS_READY_FOR_MCP_REGISTRY_PUBLISH"},
        publisher_finder=lambda: "mcp-publisher",
        runner=lambda command, timeout=300: {"ok": True},
        write_result=False,
    )

    assert result["decision"] == "HOLD_ENV_CONFIRM_REQUIRED"

