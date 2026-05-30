from ai_objective_index import aoi_030a2_final_mcp_registry_reconcile as reconcile
from ai_objective_index.aoi_030a2_marker_sync import CANONICAL_MCP_NAME, PACKAGE_NAME, TARGET_VERSION


def test_reconcile_passes_on_matching_registry_entry():
    body = f"{CANONICAL_MCP_NAME} {PACKAGE_NAME} {TARGET_VERSION}"

    result = reconcile.run_final_mcp_registry_reconcile(
        publish_result={"decision": "PASS_MCP_REGISTRY_PUBLISH_CONFIRMED", "submission_performed": True},
        fetcher=lambda: {"checked": True, "status_code": 200, "body": body, "error": ""},
        write_result=False,
    )

    assert result["decision"] == "PASS_MCP_REGISTRY_ENTRY_VERIFIED"


def test_reconcile_holds_for_registry_propagation_after_publish():
    result = reconcile.run_final_mcp_registry_reconcile(
        publish_result={"decision": "PASS_MCP_REGISTRY_PUBLISH_CONFIRMED", "submission_performed": True},
        fetcher=lambda: {"checked": True, "status_code": 200, "body": "", "error": ""},
        write_result=False,
    )

    assert result["decision"] == "HOLD_REGISTRY_PROPAGATION"


def test_reconcile_holds_without_publish():
    result = reconcile.run_final_mcp_registry_reconcile(
        publish_result={"decision": "HOLD_ENV_CONFIRM_REQUIRED", "submission_performed": False},
        write_result=False,
    )

    assert result["decision"] == "HOLD_REGISTRY_PUBLISH_NOT_CONFIRMED"

