from ai_objective_index.agent_adoption.freshness_policy import freshness_fields, negative_cache_contract


def test_freshness_fields_include_staleness_rugpull_and_recheck_policy():
    fields = freshness_fields(stale=True, rugpull_status="suspicious_diff_requires_review", negative_cache_hit=True)

    assert fields["freshness_status"] == "stale_review_required"
    assert fields["rugpull_diff_status"] == "suspicious_diff_requires_review"
    assert fields["known_negative_cache_hit"] is True
    assert "Recheck" in fields["recheck_policy"]


def test_negative_cache_is_recheckable_not_permanent_proof():
    contract = negative_cache_contract("bad-candidate")

    assert contract["known_negative_cache_hit"] is True
    assert contract["permanent_proof"] is False
    assert contract["recheckable_route_artifact"] is True
