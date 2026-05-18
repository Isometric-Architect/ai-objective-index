from ai_objective_index import mcp_runtime


def test_mcp_runtime_import_safe_and_status_clear():
    status = mcp_runtime.runtime_status()

    assert status["server_name"] == "ai-objective-index"
    assert status["read_only"] is True
    assert "search" in status["tools"]
    assert "fetch" in status["tools"]
    if not status["mcp_sdk_available"]:
        assert "MCP SDK not installed" in status["fallback_message"]


def test_build_server_returns_none_when_sdk_missing_or_server_when_available():
    server = mcp_runtime.build_server()
    if mcp_runtime.mcp_sdk_available():
        assert server is not None
    else:
        assert server is None
