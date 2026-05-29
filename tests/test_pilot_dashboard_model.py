from ai_objective_index.portfolio.pilot_dashboard_model import PilotDashboard, PilotStatusCard, dashboard_to_jsonable


def test_dashboard_model_serializes():
    card = PilotStatusCard(
        vertical="agentsec",
        display_name="AgentSec Gate",
        reviewed_object="manifest",
        primary_decision="BLOCK_FORBIDDEN_ACTION",
        allow_count=1,
        hold_count=1,
        block_count=1,
        redaction_status="PASS_REDACTED",
        feedback_status="incorporated",
        second_run_status="READY_FOR_LOCAL_SECOND_RUN",
        latest_gate_status="PASS_FIRST_AGENTSEC_PILOT_RECEIPT_READY",
        top_hold_reason="permission scope",
        top_block_reason="forbidden action",
        next_action="local owner artifact pilot",
    )
    dashboard = PilotDashboard(dashboard_id="test-dashboard", vertical_status_cards=[card.model_dump()])
    payload = dashboard_to_jsonable(dashboard)
    assert payload["schema"] == "ResidualOps_PilotDashboard/v0.1"
    assert payload["claim_boundary"]["static_local_only"] is True
