from ai_objective_index import aoi_mcp_registry_recovery_reconcile as reconcile
from ai_objective_index.aoi_030a2_marker_sync import CANONICAL_MCP_NAME, PACKAGE_NAME, TARGET_VERSION


def test_recovery_reconcile_passes_on_matching_entry():
    body = f"{CANONICAL_MCP_NAME} {PACKAGE_NAME} {TARGET_VERSION}"

    result = reconcile.run_recovery_reconcile(
        publish_result={"decision": "PASS_MCP_REGISTRY_RECOVERY_PUBLISHED", "submission_performed": True},
        fetcher=lambda: {"checked": True, "status_code": 200, "body": body, "error": ""},
        write_result=False,
    )

    assert result["decision"] == "PASS_MCP_REGISTRY_RECOVERY_RECONCILED"


def test_recovery_reconcile_holds_without_publish():
    result = reconcile.run_recovery_reconcile(
        publish_result={"decision": "HOLD_ENV_CONFIRM_REQUIRED", "submission_performed": False},
        write_result=False,
    )

    assert result["decision"] == "HOLD_PUBLISH_NOT_CONFIRMED"


def test_recovery_reconcile_mismatch_blocks():
    result = reconcile.run_recovery_reconcile(
        publish_result={"decision": "PASS_MCP_REGISTRY_RECOVERY_PUBLISHED", "submission_performed": True},
        fetcher=lambda: {"checked": True, "status_code": 200, "body": CANONICAL_MCP_NAME, "error": ""},
        write_result=False,
    )

    assert result["decision"] == "BLOCK_METADATA_MISMATCH"
