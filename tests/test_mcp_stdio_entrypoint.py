from ai_objective_index import mcp_runtime
from ai_objective_index.mcp_stdio_entrypoint import main


def test_stdio_entrypoint_fallback_does_not_crash(capsys):
    if mcp_runtime.mcp_sdk_available():
        status = mcp_runtime.runtime_status()
        assert status["mcp_sdk_available"] is True
        return

    main()
    captured = capsys.readouterr()
    assert "MCP SDK not installed" in captured.out
    assert "search" in captured.out
    assert "fetch" in captured.out
