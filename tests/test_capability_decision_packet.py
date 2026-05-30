from ai_objective_index.agent_adoption.capability_decision_packet import (
    REQUIRED_FIELDS,
    sample_capability_decision_packet,
    validate_capability_decision_packet,
)


def test_capability_decision_packet_has_required_fields_and_validates():
    packet = sample_capability_decision_packet()

    assert all(field in packet for field in REQUIRED_FIELDS)
    assert validate_capability_decision_packet(packet) == []


def test_capability_decision_packet_does_not_turn_fit_into_authorization():
    packet = sample_capability_decision_packet()

    assert packet["objective_fit_score"] > 0
    assert packet["trusted_state"] == "not_verified"
    assert packet["authorized_state"] == "not_authorized"
    assert packet["executable_state"] == "not_executable"
    assert packet["external_action_authorization"] is False
    assert packet["security_certification"] is False
    assert packet["product_readiness_claim"] is False
