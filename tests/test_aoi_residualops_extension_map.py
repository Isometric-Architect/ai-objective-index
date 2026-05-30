from ai_objective_index.agent_adoption.residualops_extension_map import (
    build_residualops_extension_map,
    route_for_issue,
)


def test_residualops_extension_map_routes_tool_code_data():
    assert route_for_issue("tool manifest permission concern") == "AgentSec"
    assert route_for_issue("patch diff CI release concern") == "QIRA"
    assert route_for_issue("dataset privacy license eval concern") == "DataCapsule"


def test_residualops_extension_map_declares_public_and_enterprise_roles():
    payload = build_residualops_extension_map()

    assert payload["aoi_role"] == "agent_and_developer_facing_public_discovery_router"
    assert payload["residualops_role"] == "enterprise_and_operator_facing_governance_layer"
    assert payload["private_kernel_not_disclosed"] is True

