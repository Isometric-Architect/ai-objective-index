from ai_objective_index import mcp_registry_submit_reconcile as reconcile
from ai_objective_index.package_metadata_audit import MCP_NAME
from ai_objective_index.real_pypi_upload_gate import PACKAGE_NAME, TARGET_VERSION


def test_reconcile_registry_entry_found_passes(monkeypatch):
    monkeypatch.setattr(reconcile, "_read_json", lambda path: {"result_token": "PUBLISH_SUCCESS", "submission_performed": True})
    body = f"{MCP_NAME} {TARGET_VERSION} {PACKAGE_NAME}"

    result = reconcile.run_mcp_registry_submit_reconcile(
        fetcher=lambda: {"checked": True, "status_code": 200, "body": body, "error": ""},
        write_result=False,
    )

    assert result["decision"] == "PASS_REGISTRY_ENTRY_VERIFIED"


def test_reconcile_not_visible_holds_propagation(monkeypatch):
    monkeypatch.setattr(reconcile, "_read_json", lambda path: {"result_token": "PUBLISH_SUCCESS", "submission_performed": True})

    result = reconcile.run_mcp_registry_submit_reconcile(
        fetcher=lambda: {"checked": True, "status_code": 200, "body": "[]", "error": ""},
        write_result=False,
    )

    assert result["decision"] == "HOLD_REGISTRY_PROPAGATION"


def test_reconcile_mismatch_blocks(monkeypatch):
    monkeypatch.setattr(reconcile, "_read_json", lambda path: {"result_token": "PUBLISH_SUCCESS", "submission_performed": True})

    result = reconcile.run_mcp_registry_submit_reconcile(
        fetcher=lambda: {"checked": True, "status_code": 200, "body": MCP_NAME, "error": ""},
        write_result=False,
    )

    assert result["decision"] == "BLOCK_METADATA_MISMATCH"
