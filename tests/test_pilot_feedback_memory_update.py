from ai_objective_index.portfolio.pilot_feedback_classifier import classify_feedback
from ai_objective_index.portfolio.pilot_feedback_memory_update import build_feedback_memory_update
from ai_objective_index.portfolio.pilot_feedback_packet import sample_feedback_packets


def test_feedback_memory_update_validates():
    packet = sample_feedback_packets()[2]
    update = build_feedback_memory_update(packet, classify_feedback(packet))
    assert update.schema_id == "ResidualOps_PilotFeedbackMemoryUpdate/v0.1"
    assert update.memory_status == "pending"
    assert update.update_type == "add_fixture_candidate"
