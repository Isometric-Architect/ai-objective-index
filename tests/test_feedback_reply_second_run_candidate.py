from ai_objective_index.portfolio.feedback_reply_classifier import classify_feedback_reply
from ai_objective_index.portfolio.feedback_reply_packet import FeedbackReplyPacket
from ai_objective_index.portfolio.feedback_reply_router import route_feedback_reply
from ai_objective_index.portfolio.feedback_reply_second_run_candidate import build_second_run_candidate


def test_second_run_candidate_generated_when_allowed():
    packet = FeedbackReplyPacket(
        reply_id="reply-second-run",
        related_vertical="qira",
        reply_text_redacted="I consent to local review and request a second local pass for the QIRA CI evidence finding.",
        consent_signal="explicit_local_review_allowed",
        requested_action="request_second_run",
    )
    classification = classify_feedback_reply(packet)
    route = route_feedback_reply(packet, classification)
    candidate = build_second_run_candidate(packet, classification, route)
    assert candidate.readiness == "READY_FOR_LOCAL_SECOND_RUN"
    assert candidate.execute_now is False
