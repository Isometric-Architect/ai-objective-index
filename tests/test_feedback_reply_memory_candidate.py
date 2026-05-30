from ai_objective_index.portfolio.feedback_reply_classifier import classify_feedback_reply
from ai_objective_index.portfolio.feedback_reply_memory_candidate import build_memory_candidate
from ai_objective_index.portfolio.feedback_reply_packet import FeedbackReplyPacket
from ai_objective_index.portfolio.feedback_reply_router import route_feedback_reply


def test_memory_candidate_generated():
    packet = FeedbackReplyPacket(
        reply_id="reply-memory",
        related_vertical="portfolio",
        reply_text_redacted="Please clarify the portfolio readout next action in the local artifact.",
        consent_signal="sample_fixture",
        requested_action="clarify",
    )
    classification = classify_feedback_reply(packet)
    route = route_feedback_reply(packet, classification)
    candidate = build_memory_candidate(packet, classification, route)
    assert candidate.status == "pending_review"
    assert candidate.vertical == "portfolio"
