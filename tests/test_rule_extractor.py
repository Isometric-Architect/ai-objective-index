from ai_objective_index.extractor.rule_extractor import (
    extract_docs_fields,
    extract_policy_fields,
    extract_pricing_fields,
    extract_tool_fields,
)


def test_rule_extractor_detects_free_plan() -> None:
    fields = extract_pricing_fields("Free plan includes 100 requests. Paid usage starts at $9.")

    assert fields["free_plan_found"] is True
    assert fields["starting_price_usd"] == 9.0


def test_rule_extractor_detects_api_docs() -> None:
    fields = extract_docs_fields("API reference and SDK docs", links=["https://example.com/docs"])

    assert fields["api_available"] is True
    assert fields["docs_url_found"] is True


def test_rule_extractor_detects_commercial_use() -> None:
    fields = extract_policy_fields("Commercial use is allowed under the terms of service.")

    assert fields["commercial_use_found"] is True
    assert fields["terms_url_found"] is True


def test_rule_extractor_detects_mcp_support() -> None:
    fields = extract_tool_fields(
        {
            "title": "BrowserPilot MCP Server",
            "text": "Open source Model Context Protocol MCP server for browser automation.",
            "links": ["https://github.com/example/browser-mcp-server"],
            "page_type": "github_readme",
        }
    )

    assert fields["mcp_support"] is True
    assert "mcp_support" in fields["capabilities"]

