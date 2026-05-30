from ai_objective_index.agent_adoption.discover_mode import discover_capabilities
from ai_objective_index.agent_adoption.mcp_adapters import (
    discover_capabilities_for_objective,
    preflight_capability_for_use,
)
from ai_objective_index.agent_adoption.preflight_mode import preflight_capability


def test_discover_and_preflight_responses_include_backward_compatible_cdp():
    discover = discover_capabilities()
    preflight = preflight_capability()

    assert "top_candidates" in discover
    assert "route_decision" in discover
    assert "capability_decision_packet" in discover
    assert "missing_fields" in preflight
    assert "capability_decision_packet" in preflight


def test_mcp_adapters_include_cdp_and_remain_read_only():
    discover = discover_capabilities_for_objective("find MCP", "mcp discovery")
    preflight = preflight_capability_for_use("candidate", "read-only review")

    assert discover["read_only"] is True
    assert preflight["read_only"] is True
    assert discover["action_authorization"] is False
    assert preflight["action_authorization"] is False
    assert "capability_decision_packet" in discover
    assert "capability_decision_packet" in preflight
