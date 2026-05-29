from ai_objective_index.portfolio.pilot_intake_packet import PilotIntakePacket, intake_packet_to_jsonable


def test_intake_packet_serializes():
    packet = PilotIntakePacket(intake_id="intake-1", pilot_label="sample")
    payload = intake_packet_to_jsonable(packet)
    assert payload["schema"] == "ResidualOps_PilotIntakePacket/v0.1"
    assert payload["allowed_review_scope"]["external_network"] is False
    assert payload["claim_boundary"]["no_external_action_authorization"] is True
