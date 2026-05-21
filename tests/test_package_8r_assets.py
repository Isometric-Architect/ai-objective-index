from pathlib import Path


def test_package_8r_assets_exist():
    assert Path("docs/package_8r_mcp_registry_publish.md").exists()
    assert Path("docs/mcp_registry_publish_safety.md").exists()
    assert Path("docs/mcp_registry_after_publish.md").exists()
    assert Path("public_launch/wave11_mcp_registry/MCP_REGISTRY_TOKEN_SAFETY_NOTE.md").exists()
    assert Path("public_launch/wave11_mcp_registry/MCP_REGISTRY_VERSION_UPDATE_PLAN.md").exists()


def test_mcp_registry_token_safety_note_says_no_token_in_chat():
    text = Path("public_launch/wave11_mcp_registry/MCP_REGISTRY_TOKEN_SAFETY_NOTE.md").read_text(encoding="utf-8")

    assert "Do not paste GitHub tokens into ChatGPT/Codex chat." in text
