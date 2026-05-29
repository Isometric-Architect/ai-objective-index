from ai_objective_index.portfolio.pilot_feedback_packet import feedback_packet_to_jsonable, sample_feedback_packets


def test_feedback_packet_serializes():
    packet = sample_feedback_packets()[0]
    payload = feedback_packet_to_jsonable(packet)
    assert payload["schema"] == "ResidualOps_PilotFeedbackPacket/v0.1"
    assert payload["vertical"] == "agentsec"
    assert payload["claim_boundary"]["no_external_action_authorization"] is True
