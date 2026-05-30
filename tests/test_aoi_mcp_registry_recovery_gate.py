from ai_objective_index import aoi_mcp_registry_recovery_gate as gate
from ai_objective_index.aoi_030a2_marker_sync import CANONICAL_MCP_NAME, MCP_MARKER, PACKAGE_NAME, TARGET_VERSION


def _state():
    return {
        "server_name": CANONICAL_MCP_NAME,
        "server_version": TARGET_VERSION,
        "server_package_registry_type": "pypi",
        "server_package_identifier": PACKAGE_NAME,
        "server_package_version": TARGET_VERSION,
    }


def test_recovery_gate_passes_when_verified_and_validate_ok(monkeypatch):
    monkeypatch.setattr(gate, "run_marker_sync", lambda write_result=True: {"decision": "PASS_MARKER_SYNCED_030A2"})
    monkeypatch.setattr(gate, "current_marker_state", _state)
    monkeypatch.setattr(gate, "read_json", lambda path: {"decision": "PASS_PYPI_030A2_VERIFIED"})
    monkeypatch.setattr(gate, "read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(gate, "_claim_guard_passed", lambda: True)
    monkeypatch.setattr(gate, "_tech_protection_passed", lambda: True)

    result = gate.run_recovery_gate(
        runner=lambda command, timeout=120: {"ok": True, "returncode": 0, "stdout": "valid", "stderr": ""},
        publisher_finder=lambda: "mcp-publisher",
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "PASS_READY_FOR_MCP_REGISTRY_RECOVERY_PUBLISH"


def test_recovery_gate_holds_before_pypi_verify(monkeypatch):
    monkeypatch.setattr(gate, "run_marker_sync", lambda write_result=True: {"decision": "PASS_MARKER_SYNCED_030A2"})
    monkeypatch.setattr(gate, "current_marker_state", _state)
    monkeypatch.setattr(gate, "read_json", lambda path: {"decision": "HOLD_PYPI_UPLOAD_NOT_CONFIRMED"})
    monkeypatch.setattr(gate, "read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(gate, "_claim_guard_passed", lambda: True)
    monkeypatch.setattr(gate, "_tech_protection_passed", lambda: True)

    result = gate.run_recovery_gate(publisher_finder=lambda: "mcp-publisher", token_scanner=lambda: [], write_result=False)

    assert result["decision"] == "HOLD_PYPI_VERIFY_REQUIRED"


def test_recovery_gate_server_json_invalid_blocks(monkeypatch):
    monkeypatch.setattr(gate, "run_marker_sync", lambda write_result=True: {"decision": "PASS_MARKER_SYNCED_030A2"})
    monkeypatch.setattr(gate, "current_marker_state", _state)
    monkeypatch.setattr(gate, "read_json", lambda path: {"decision": "PASS_PYPI_030A2_VERIFIED"})
    monkeypatch.setattr(gate, "read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(gate, "_claim_guard_passed", lambda: True)
    monkeypatch.setattr(gate, "_tech_protection_passed", lambda: True)

    result = gate.run_recovery_gate(
        runner=lambda command, timeout=120: {"ok": False, "returncode": 1, "stdout": "", "stderr": "SERVER_JSON_INVALID"},
        publisher_finder=lambda: "mcp-publisher",
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "BLOCK_SERVER_JSON_INVALID"
