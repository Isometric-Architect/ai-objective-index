from ai_objective_index import mcp_registry_post_publish_verify as verify
from ai_objective_index.package_metadata_audit import MCP_NAME


def test_post_publish_verify_found_passes():
    result = verify.run_mcp_registry_post_publish_verify(
        fetcher=lambda: {"checked": True, "status_code": 200, "body": MCP_NAME},
        write_result=False,
    )

    assert result["decision"] == "PASS_REGISTRY_ENTRY_FOUND"


def test_post_publish_verify_not_found_holds():
    result = verify.run_mcp_registry_post_publish_verify(
        fetcher=lambda: {"checked": True, "status_code": 200, "body": "[]"},
        write_result=False,
    )

    assert result["decision"] == "HOLD_REGISTRY_ENTRY_NOT_FOUND_YET"


def test_post_publish_verify_network_unavailable_holds():
    result = verify.run_mcp_registry_post_publish_verify(
        fetcher=lambda: {"checked": False, "status_code": None, "body": "", "error": "offline"},
        write_result=False,
    )

    assert result["decision"] == "HOLD_REGISTRY_VERIFY_NOT_CHECKED"
