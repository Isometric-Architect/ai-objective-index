from ai_objective_index.portfolio.pilot_intake_packet import PilotIntakePacket, ProvidedArtifact
from ai_objective_index.portfolio.pilot_run_plan import build_run_plan, run_plan_to_jsonable
from ai_objective_index.portfolio.pilot_vertical_router import route_intake_packet


def test_run_plan_sample_ready_for_agentsec():
    packet = PilotIntakePacket(
        intake_id="intake-agentsec",
        pilot_label="sample",
        provided_artifact=ProvidedArtifact(artifact_type="mcp_manifest"),
    )
    plan = build_run_plan(route_intake_packet(packet), consent_status="sample_fixture")
    payload = run_plan_to_jsonable(plan)
    assert payload["schema"] == "ResidualOps_PilotRunPlan/v0.1"
    assert payload["receipt_target"] == "agentsec_pilot_receipt"
    assert payload["run_status"] == "READY_FOR_LOCAL_SAMPLE"
