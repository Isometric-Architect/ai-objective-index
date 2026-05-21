import subprocess

from ai_objective_index import mcp_publisher_setup


def test_mcp_publisher_setup_missing_cli_holds(monkeypatch):
    monkeypatch.setattr(mcp_publisher_setup.shutil, "which", lambda name: None)

    result = mcp_publisher_setup.run_mcp_publisher_setup(write_result=False)

    assert result["decision"] == "HOLD_MCP_PUBLISHER_MISSING"
    assert result["mcp_publisher_available"] is False
    assert result["token_printed"] is False


def test_mcp_publisher_setup_available_passes(monkeypatch):
    class Completed:
        returncode = 0
        stdout = "mcp-publisher help"
        stderr = ""

    monkeypatch.setattr(mcp_publisher_setup.shutil, "which", lambda name: "mcp-publisher")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Completed())

    result = mcp_publisher_setup.run_mcp_publisher_setup(write_result=False)

    assert result["decision"] == "PASS_MCP_PUBLISHER_AVAILABLE"
    assert result["mcp_publisher_available"] is True


def test_mcp_publisher_setup_unsafe_binary_source_blocks():
    result = mcp_publisher_setup.run_mcp_publisher_setup(
        mode="download-windows",
        download_url="https://example.invalid/mcp-publisher.exe",
        write_result=False,
    )

    assert result["decision"] == "BLOCK_UNSAFE_BINARY_SOURCE"
    assert result["download_performed"] is False
