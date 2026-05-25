from ai_objective_index.agentsec.package4 import run_agentsec4_package


def test_agentsec4_package_runs_without_external_actions():
    result = run_agentsec4_package()

    assert result["decision"] == "PASS_AGENTSEC4_POLICY_PACK_AND_MCP_HARDENING"
    assert result["network_used"] is False
    assert result["external_tool_executed"] is False
    assert result["can_authorize_action"] is False
