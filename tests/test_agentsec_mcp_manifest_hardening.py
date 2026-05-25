import json
from pathlib import Path

from ai_objective_index.agentsec.mcp_manifest_hardening import (
    build_mcp_manifest_hardening_result,
    write_mcp_manifest_hardening_result,
)


def test_agentsec4_mcp_manifest_hardening_passes_current_manifest():
    result = build_mcp_manifest_hardening_result()

    assert result["decision"] == "PASS_AGENTSEC4_MCP_MANIFEST_HARDENED"
    assert result["tool_count"] > 0
    assert result["live_mcp_called"] is False


def test_agentsec4_mcp_manifest_hardening_blocks_non_read_only_tool(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / ".mcp").mkdir()
    (tmp_path / "data" / "generated_mcp_tools_manifest.json").write_text(
        json.dumps({"read_only": True, "tools": [{"name": "send_email", "read_only": False}]}),
        encoding="utf-8",
    )
    (tmp_path / ".mcp" / "server.json").write_text(
        json.dumps(
            {
                "read_only": True,
                "limitations": ["not verified", "not security certified", "not a quality guarantee"],
                "vnext_surfaces": {
                    "external_action_authorization": False,
                    "external_tool_execution": False,
                    "live_mcp_calls": False,
                },
            }
        ),
        encoding="utf-8",
    )

    result = build_mcp_manifest_hardening_result(root=tmp_path)

    assert result["decision"] == "BLOCK_AGENTSEC4_MCP_MANIFEST_RISK"
    assert any("read_only" in finding for finding in result["findings"])


def test_agentsec4_mcp_manifest_hardening_writes_outputs():
    result = write_mcp_manifest_hardening_result()

    assert result["decision"] == "PASS_AGENTSEC4_MCP_MANIFEST_HARDENED"
