from ai_objective_index.portfolio.feedback_reply_packet import FeedbackReplyPacket, packet_to_jsonable


def test_feedback_reply_packet_serializes():
    packet = FeedbackReplyPacket(
        reply_id="reply-1",
        source="sample_fixture",
        reply_text_redacted="Please clarify the manifest finding.",
        consent_signal="sample_fixture",
        requested_action="clarify",
    )
    payload = packet_to_jsonable(packet)
    assert payload["schema"] == "ResidualOps_FeedbackReplyPacket/v0.1"
    assert payload["reply_id"] == "reply-1"
    assert payload["claim_boundary"]["not_security_certification"] is True
