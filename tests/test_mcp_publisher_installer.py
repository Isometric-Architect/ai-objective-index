import subprocess

from ai_objective_index import mcp_publisher_installer as installer


def test_installer_missing_binary_holds(monkeypatch):
    monkeypatch.setattr(installer.shutil, "which", lambda name: None)
    monkeypatch.setattr(installer, "local_publisher_path", lambda: installer.Path("missing.exe"))

    result = installer.run_mcp_publisher_installer(write_result=False)

    assert result["decision"] == "HOLD_MCP_PUBLISHER_MISSING"


def test_installer_mocked_binary_help_passes(monkeypatch):
    class Completed:
        returncode = 0
        stdout = "help"
        stderr = ""

    monkeypatch.setattr(installer, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: Completed())

    result = installer.run_mcp_publisher_installer(write_result=False)

    assert result["decision"] == "PASS_MCP_PUBLISHER_AVAILABLE"


def test_download_requires_env_confirmation():
    result = installer.run_mcp_publisher_installer(mode="download-windows", env={}, write_result=False)

    assert result["decision"] == "HOLD_MANUAL_INSTALL_REQUIRED"
    assert result["download_performed"] is False


def test_unsafe_download_source_blocks():
    result = installer.run_mcp_publisher_installer(
        mode="download-windows",
        env={installer.DOWNLOAD_CONFIRM_ENV: "YES"},
        asset_url="https://example.invalid/mcp-publisher_windows_amd64.tar.gz",
        write_result=False,
    )

    assert result["decision"] == "BLOCK_UNSAFE_BINARY_SOURCE"
