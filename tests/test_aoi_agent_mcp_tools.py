from ai_objective_index import mcp_tools
from ai_objective_index.agent_adoption.agent_adoption_packager import package_agent_adoption
from ai_objective_index.mcp_manifest import get_mcp_tool_manifest


def test_get_aoi_capability_card_tool_is_read_only():
    payload = mcp_tools.get_aoi_capability_card()

    assert payload["read_only"] is True
    assert payload["action_authorization"] is False
    assert payload["capability_card"]["type"] == "objective_to_capability_discovery_and_preuse_trust_router"


def test_discover_capabilities_for_objective_tool_returns_useful_hold_candidates():
    payload = mcp_tools.discover_capabilities_for_objective(
        objective="Find a read-only capability discovery helper.",
        query="MCP discovery source traces",
    )

    assert payload["read_only"] is True
    assert payload["external_api_used"] is False
    assert payload["route_decision"] == "HOLD_WITH_ACTIONABLE_NEXT_STEPS"
    assert payload["top_candidates"]
    assert payload["next_action"]


def test_preflight_capability_for_use_tool_blocks_external_action():
    payload = mcp_tools.preflight_capability_for_use(
        candidate_id="aoi-read-only-mcp-tools",
        intended_use="Execute the tool and publish results.",
        available_metadata={"permission_scope": "read-only"},
    )

    assert payload["read_only"] is True
    assert payload["route_decision"] == "BLOCK_EXTERNAL_ACTION"
    assert payload["action_authorization"] is False


def test_explain_aoi_agent_use_includes_when_to_use_and_boundaries():
    package_agent_adoption()
    payload = mcp_tools.explain_aoi_agent_use()

    assert payload["read_only"] is True
    assert "When To Use AOI" in payload["when_to_use"]
    assert "When Not To Use AOI" in payload["when_not_to_use"]
    assert payload["external_action_authorization"] is False


def test_mcp_manifest_includes_agent_tools_as_read_only():
    manifest = get_mcp_tool_manifest()
    tools = {tool["name"]: tool for tool in manifest["tools"]}

    for name in {
        "get_aoi_capability_card",
        "discover_capabilities_for_objective",
        "preflight_capability_for_use",
        "explain_aoi_agent_use",
        "list_aoi_agent_examples",
    }:
        assert tools[name]["read_only"] is True
