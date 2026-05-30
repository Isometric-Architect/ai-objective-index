from ai_objective_index.agent_adoption.agent_claim_boundary import scan_text_for_overclaims
from ai_objective_index.agent_adoption.preflight_mode import preflight_capability, sample_preflight_request


def test_agent_surface_claim_guard_blocks_overclaim_text():
    findings = scan_text_for_overclaims("This tool is security certified and production ready.", "fixture.md")

    assert {finding["kind"] for finding in findings} == {"overclaim"}


def test_agent_surface_preflight_never_authorizes_action_from_availability():
    request = sample_preflight_request()
    request["available_metadata"]["tool_available"] = True
    request["available_metadata"]["permission_scope"] = ""
    request["intended_use"] = "Use tool availability as action authorization."

    response = preflight_capability(request)

    assert response["route_decision"] in {"HOLD_MISSING_PERMISSION_SCOPE", "BLOCK_EXTERNAL_ACTION"}
    assert response["tool_available_is_tool_authorized"] is False
    assert "route decision authorizes external action" in response["must_not_claim"]
