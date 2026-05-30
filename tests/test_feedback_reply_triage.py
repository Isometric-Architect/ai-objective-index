from ai_objective_index.portfolio.feedback_reply_classifier import classify_feedback_reply
from ai_objective_index.portfolio.feedback_reply_packet import FeedbackReplyPacket
from ai_objective_index.portfolio.feedback_reply_router import route_feedback_reply
from ai_objective_index.portfolio.feedback_reply_triage import build_triage_entry


def test_triage_entry_generated():
    packet = FeedbackReplyPacket(
        reply_id="reply-triage",
        related_vertical="agentsec",
        reply_text_redacted="Please clarify the tool manifest finding in the local readout.",
        consent_signal="sample_fixture",
        requested_action="clarify",
    )
    classification = classify_feedback_reply(packet)
    route = route_feedback_reply(packet, classification)
    triage = build_triage_entry(packet, classification, route)
    assert triage.status == "routed"
    assert triage.memory_candidate is True
