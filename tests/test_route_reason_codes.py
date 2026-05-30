from ai_objective_index.agent_adoption.route_reason_codes import ROUTE_REASON_CODES, reason_codes_for_route


def test_route_reason_codes_include_required_machine_codes():
    for code in (
        "OBJECTIVE_MATCH",
        "SOURCE_TRACE_PRESENT",
        "METADATA_INCOMPLETE",
        "PERMISSION_SCOPE_UNKNOWN",
        "STALE_METADATA",
        "RUGPULL_DIFF_SUSPECTED",
        "NEGATIVE_CACHE_HIT",
        "DESTRUCTIVE_ACTION",
        "SECRET_LIKE_INPUT",
        "ACTION_AUTHORIZATION_OVERCLAIM",
        "TOOL_RISK_REQUIRES_AGENTSEC",
        "CODE_RELEASE_REQUIRES_QIRA",
        "DATA_USE_REQUIRES_DATACAPSULE",
    ):
        assert code in ROUTE_REASON_CODES


def test_route_reason_codes_map_blocks_and_escalations():
    assert "DESTRUCTIVE_ACTION" in reason_codes_for_route("BLOCK_DESTRUCTIVE_ACTION")
    assert "TOOL_RISK_REQUIRES_AGENTSEC" in reason_codes_for_route("ESCALATE_AGENTSEC")
    assert "DATA_USE_REQUIRES_DATACAPSULE" in reason_codes_for_route("ESCALATE_DATACAPSULE")
