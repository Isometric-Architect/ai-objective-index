from ai_objective_index.portfolio.pilot_link_pack import KNOWN_LINKS, build_link_pack_markdown, write_link_pack


def test_link_pack_uses_known_links_and_todo_for_unknown():
    markdown = build_link_pack_markdown()
    assert "https://github.com/Isometric-Architect/ai-objective-index" in markdown
    assert "https://pypi.org/project/ai-objective-index/0.3.0a1/" in markdown
    assert "TODO: MCP Registry submission is not completed." in markdown
    assert KNOWN_LINKS["mcp_registry_entry"].startswith("TODO")


def test_link_pack_written_without_external_action():
    payload = write_link_pack()
    assert payload["uses_todo_for_unknown"] is True
    assert payload["auto_post_performed"] is False
    assert payload["external_api_used"] is False
