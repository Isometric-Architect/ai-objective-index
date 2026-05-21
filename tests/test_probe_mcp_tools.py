from ai_objective_index.vnext import probe_mcp_tools


def test_probe_mcp_plan_tool_is_offline():
    result = probe_mcp_tools.plan_probe_before_use(
        query="image API",
        objective="select source-traced candidates",
        data_scope="sample",
        limit=1,
    )
    assert result["read_only"] is True
    assert result["live_mcp_call"] is False


def test_probe_mcp_route_with_probes_is_conservative():
    result = probe_mcp_tools.route_objective_with_probes(
        query="image API",
        objective="select source-traced candidates",
        data_scope="sample",
        limit=1,
        run_local_probes=False,
    )
    assert result["external_tool_execution"] is False
    assert "probe_route_overlay" in result
