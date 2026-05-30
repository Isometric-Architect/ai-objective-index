from ai_objective_index.agent_adoption.route_transition_policy import (
    allowed_action_for_route,
    transition_allowed,
    validate_state_separation,
)


def test_state_separation_enforced_on_packets():
    packet = {
        "discovered_state": "discovered",
        "trusted_state": "not_verified",
        "authorized_state": "not_authorized",
        "executable_state": "not_executable",
    }
    assert validate_state_separation(packet) == []

    bad = {**packet, "trusted_state": "trusted", "authorized_state": "authorized"}
    assert "trusted_cannot_imply_authorized" in validate_state_separation(bad)


def test_hold_to_allow_requires_new_evidence():
    assert transition_allowed("HOLD_AUTHORIZATION", "ALLOW_READ_ONLY", new_evidence_attached=False) is False
    assert transition_allowed("HOLD_AUTHORIZATION", "ALLOW_READ_ONLY", new_evidence_attached=True) is True
    assert transition_allowed("BLOCK_DESTRUCTIVE_ACTION", "ALLOW_READ_ONLY", new_evidence_attached=True) is False
    assert allowed_action_for_route("ALLOW_DRAFT_ONLY")["allows_send"] is False
