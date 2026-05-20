from ai_objective_index import mcp_tools


def test_mcp_route_objective_returns_read_only_result():
    result = mcp_tools.route_objective(
        query="image API",
        objective="select source-traced API candidates",
        domain="ai_apis",
        data_scope="sample",
        limit=2,
    )
    assert result["read_only"] is True
    assert result["probe_execution"] is False
    assert result["external_tool_execution"] is False
    assert result["route_summary"]["total_candidates"] <= 2


def test_mcp_get_capability_trust_and_explain_route_decision():
    trust = mcp_tools.get_capability_trust("capability:aoi-pixelforge-api", data_scope="sample")
    assert trust["read_only"] is True
    assert trust["found"] is True
    explanation = mcp_tools.explain_route_decision("capability:aoi-pixelforge-api", data_scope="sample")
    assert explanation["read_only"] is True
    assert explanation["probe_execution"] is False
    assert "must_not_claim" in explanation
