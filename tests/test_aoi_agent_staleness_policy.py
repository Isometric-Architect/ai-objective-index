from ai_objective_index.agent_adoption.agent_staleness_policy import build_staleness_policy, freshness_for_sample


def test_staleness_policy_does_not_claim_live_freshness():
    policy = build_staleness_policy()
    sample = policy["sample_freshness"]

    assert sample["live_check_performed"] is False
    assert sample["needs_refresh"] is True
    assert "Do not claim live freshness" in policy["rules"][0]


def test_freshness_sample_has_required_fields():
    freshness = freshness_for_sample()

    for key in [
        "last_checked_at",
        "source_trace_age",
        "registry_payload_version",
        "stale_warning",
        "needs_refresh",
        "refresh_next_action",
    ]:
        assert key in freshness

