from ai_objective_index.vnext.objective_router_models import ObjectiveRouteRequest
from ai_objective_index.vnext.probe_card import ProbeReceipt, ProbeResult
from ai_objective_index.vnext.probe_route_adapter import overlay_probe_results, route_objective_with_probes


def test_probe_overlay_cannot_upgrade_hold_to_allow():
    route = {
        "route_summary": {"hold_count": 1},
        "results": [
            {
                "capability_id": "capability:test",
                "route_decision": {"decision": "HOLD_POLICY_CLARITY", "next_actions": []},
            }
        ],
    }
    receipt = ProbeReceipt(
        plan_id="plan",
        probe_results=[ProbeResult(probe_id="probe", capability_id="capability:test", result="PASS_LOCAL")],
    )
    overlay = overlay_probe_results(route, receipt)
    assert overlay.per_capability_probe_overlay[0].decision_effect == "DO_NOT_UPGRADE"


def test_route_objective_with_probes_returns_overlay():
    request = ObjectiveRouteRequest(query="image API", objective="select source-traced candidates", data_scope="sample", limit=1)
    payload = route_objective_with_probes(request, run_local_probes=False)
    assert "probe_route_overlay" in payload
    assert payload["network_used"] is False
