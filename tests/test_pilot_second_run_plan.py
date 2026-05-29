from ai_objective_index.portfolio.pilot_feedback_classifier import classify_feedback
from ai_objective_index.portfolio.pilot_feedback_packet import PilotFeedbackPacket, sample_feedback_packets
from ai_objective_index.portfolio.pilot_second_run_plan import build_second_run_plan


def test_second_run_plan_ready_only_for_local_redacted_consented_feedback():
    packet = sample_feedback_packets()[0]
    plan = build_second_run_plan(packet, classify_feedback(packet))
    assert plan.run_status == "READY_FOR_LOCAL_SECOND_RUN"
    assert plan.execute_now is False


def test_second_run_plan_blocks_external_action():
    packet = PilotFeedbackPacket(
        feedback_id="feedback-action",
        dry_run_id="dry-run",
        vertical="qira",
        consent_status="owner_provided",
        feedback_category="request_second_run",
        feedback_text="Deploy this package.",
        external_action_requested=True,
    )
    plan = build_second_run_plan(packet, classify_feedback(packet))
    assert plan.run_status == "BLOCK_EXTERNAL_ACTION"
