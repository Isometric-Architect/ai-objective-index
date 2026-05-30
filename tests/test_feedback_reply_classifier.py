from ai_objective_index.portfolio.feedback_reply_classifier import classify_feedback_reply
from ai_objective_index.portfolio.feedback_reply_packet import FeedbackReplyPacket


def _packet(text: str, **kwargs):
    defaults = {
        "reply_id": "reply-test",
        "source": "sample_fixture",
        "reply_text_redacted": text,
        "consent_signal": "sample_fixture",
        "requested_action": "clarify",
    }
    defaults.update(kwargs)
    return FeedbackReplyPacket(**defaults)


def test_classifier_blocks_external_action_request():
    packet = _packet("Please create a GitHub issue.", requested_action="request_external_action", external_action_requested=True)
    assert classify_feedback_reply(packet).classification == "BLOCK_EXTERNAL_ACTION_REQUEST"


def test_classifier_blocks_certification_request():
    packet = _packet("Please certify this as product ready.", requested_action="request_certification")
    assert classify_feedback_reply(packet).classification == "BLOCK_CERTIFICATION_OR_READINESS_CLAIM"


def test_classifier_blocks_token_private_data():
    packet = _packet("redacted token", token_or_secret_detected=True)
    assert classify_feedback_reply(packet).classification == "BLOCK_SECRET_OR_PRIVATE_DATA"


def test_classifier_accepts_local_second_run_with_consent():
    packet = _packet(
        "I consent to local review and request a second local pass for this finding.",
        requested_action="request_second_run",
        consent_signal="explicit_local_review_allowed",
    )
    assert classify_feedback_reply(packet).classification == "ACCEPT_SECOND_RUN_CANDIDATE"
