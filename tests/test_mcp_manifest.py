from ai_objective_index.mcp_manifest import get_mcp_tool_manifest


def test_manifest_has_required_server_metadata():
    manifest = get_mcp_tool_manifest()

    assert manifest["server_name"] == "ai-objective-index"
    assert manifest["read_only"] is True


def test_manifest_lists_all_read_only_tools():
    manifest = get_mcp_tool_manifest()
    names = {tool["name"] for tool in manifest["tools"]}

    assert names == {
        "search",
        "fetch",
        "search_objectives",
        "rank_options",
        "compare_tools",
        "explain_score",
        "get_source_trace",
        "list_missing_fields",
        "generate_decision_receipt",
    }
    assert all(tool["read_only"] is True for tool in manifest["tools"])


def test_manifest_forbidden_actions():
    manifest = get_mcp_tool_manifest()
    forbidden = set(manifest["forbidden_actions"])

    assert {
        "payment",
        "booking",
        "login",
        "email_sending",
        "purchase",
        "contract_signing",
    }.issubset(forbidden)
