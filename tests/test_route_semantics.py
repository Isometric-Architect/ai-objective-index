from ai_objective_index.agent_adoption.route_semantics import (
    EXPLICIT_SEPARATIONS,
    ROUTE_CLASSES,
    is_execution_authorizing_route,
    route_family,
    separation_claims,
)
from ai_objective_index.agent_adoption.route_transition_policy import allowed_action_for_route


def test_route_semantics_include_granular_labels_and_separations():
    for route in (
        "FOUND_ONLY",
        "ALLOW_DISCOVERY_ONLY",
        "ALLOW_READ_ONLY",
        "HOLD_STALE_METADATA",
        "HOLD_RUGPULL_DIFF",
        "BLOCK_ACTION_AUTHORIZATION_CLAIM",
        "ESCALATE_OPERATOR_POLICY",
    ):
        assert route in ROUTE_CLASSES
    assert "FOUND != TRUSTED" in EXPLICIT_SEPARATIONS
    assert "TRUSTED != AUTHORIZED" in EXPLICIT_SEPARATIONS
    assert "AUTHORIZED != EXECUTABLE" in EXPLICIT_SEPARATIONS
    assert all(value is False for value in separation_claims().values())


def test_allow_discovery_and_read_only_do_not_authorize_write_send_delete():
    discovery = allowed_action_for_route("ALLOW_DISCOVERY_ONLY")
    read_only = allowed_action_for_route("ALLOW_READ_ONLY")

    assert discovery["allows_execution"] is False
    assert read_only["allows_read"] is True
    assert read_only["allows_write"] is False
    assert read_only["allows_send"] is False
    assert read_only["action_authorization"] is False
    assert is_execution_authorizing_route("ALLOW_DISCOVERY_ONLY") is False
    assert route_family("HOLD_STALE_METADATA") == "hold"
