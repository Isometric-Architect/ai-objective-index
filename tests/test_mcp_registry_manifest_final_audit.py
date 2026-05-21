from ai_objective_index import mcp_registry_manifest_final_audit as audit
from ai_objective_index.package_metadata_audit import MCP_MARKER, MCP_NAME
from ai_objective_index.real_pypi_upload_gate import PACKAGE_NAME, TARGET_VERSION


def _server(version=TARGET_VERSION, name=MCP_NAME):
    return {
        "name": name,
        "version": version,
        "repository": {"url": audit.GITHUB_REPO_URL},
        "packages": [
            {
                "registryType": "pypi",
                "identifier": PACKAGE_NAME,
                "version": version,
                "transport": {"type": "stdio"},
            }
        ],
        "draft_not_submittable": False,
    }


def test_manifest_final_audit_passes(monkeypatch):
    monkeypatch.setattr(audit, "_read_server_json", _server)
    monkeypatch.setattr(audit, "_read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(audit, "_pypi_verified", lambda: True)
    monkeypatch.setattr(audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(audit, "_overclaim_findings", lambda paths=None: [])

    result = audit.run_mcp_registry_manifest_final_audit(write_result=False)

    assert result["decision"] == "PASS_MANIFEST_READY"


def test_manifest_final_audit_metadata_mismatch_blocks(monkeypatch):
    monkeypatch.setattr(audit, "_read_server_json", lambda: _server(version="0.3.0a0"))
    monkeypatch.setattr(audit, "_read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(audit, "_pypi_verified", lambda: True)
    monkeypatch.setattr(audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(audit, "_overclaim_findings", lambda paths=None: [])

    result = audit.run_mcp_registry_manifest_final_audit(write_result=False)

    assert result["decision"] == "BLOCK_METADATA_MISMATCH"


def test_manifest_final_audit_missing_pypi_holds(monkeypatch):
    monkeypatch.setattr(audit, "_read_server_json", _server)
    monkeypatch.setattr(audit, "_read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(audit, "_pypi_verified", lambda: False)
    monkeypatch.setattr(audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(audit, "_overclaim_findings", lambda paths=None: [])

    result = audit.run_mcp_registry_manifest_final_audit(write_result=False)

    assert result["decision"] == "HOLD_PYPI_NOT_VERIFIED"


def test_manifest_final_audit_overclaim_blocks(monkeypatch):
    monkeypatch.setattr(audit, "_read_server_json", _server)
    monkeypatch.setattr(audit, "_read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(audit, "_pypi_verified", lambda: True)
    monkeypatch.setattr(audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(audit, "_overclaim_findings", lambda paths=None: [{"path": "README.md", "phrase": "safe tool"}])

    result = audit.run_mcp_registry_manifest_final_audit(write_result=False)

    assert result["decision"] == "BLOCK_OVERCLAIM"
