from ai_objective_index.agent_adoption.capability_decision_packet import build_capability_decision_packet
from ai_objective_index.agent_adoption.hold_to_replan_loop import replan_for_hold


def test_hold_to_replan_loop_has_guards_and_no_auto_approval():
    packet = build_capability_decision_packet(
        objective="Review stale candidate",
        capability_id="stale-candidate",
        capability_name="Stale Candidate",
        route_decision="HOLD_STALE_METADATA",
    )
    result = replan_for_hold(packet, max_iterations=2)

    assert result["max_iterations"] == 2
    assert result["no_auto_approval"] is True
    assert result["no_external_action"] is True
    assert result["no_repeated_candidate_without_new_evidence"] is True
    assert "refresh source trace" in result["allowed_repair_actions"]


def test_hold_to_replan_routes_rugpull_to_review_or_alternate():
    packet = build_capability_decision_packet(
        objective="Review drifted candidate",
        capability_id="drifted",
        capability_name="Drifted",
        route_decision="HOLD_RUGPULL_DIFF",
    )
    result = replan_for_hold(packet)

    assert result["escalation_path"] == "ESCALATE_AGENTSEC"
    assert "choose alternate candidate" in result["allowed_repair_actions"]
