from ai_objective_index.portfolio.pilot_feedback_classifier import classify_feedback
from ai_objective_index.portfolio.pilot_feedback_packet import PilotFeedbackPacket, sample_feedback_packets
from ai_objective_index.portfolio.pilot_second_run_gate import evaluate_second_run_gate
from ai_objective_index.portfolio.pilot_second_run_plan import build_second_run_plan


def test_second_run_gate_ready_for_safe_sample():
    packet = sample_feedback_packets()[0]
    classification = classify_feedback(packet)
    plan = build_second_run_plan(packet, classification)
    gate = evaluate_second_run_gate(packet, classification, plan)
    assert gate.decision == "READY_FOR_LOCAL_SECOND_RUN"
    assert gate.execute_now is False


def test_second_run_gate_blocks_overclaim():
    packet = PilotFeedbackPacket(
        feedback_id="feedback-overclaim",
        dry_run_id="dry-run",
        vertical="agentsec",
        consent_status="owner_provided",
        feedback_category="request_second_run",
        feedback_text="Certify security from this feedback.",
    )
    classification = classify_feedback(packet)
    gate = evaluate_second_run_gate(packet, classification, build_second_run_plan(packet, classification))
    assert gate.decision == "BLOCK_OVERCLAIM"
