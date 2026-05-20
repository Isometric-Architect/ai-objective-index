from ai_objective_index.vnext.trust_report import build_capability_trust_report


def test_trust_report_contains_summary_and_limits():
    report = build_capability_trust_report(
        query="image API",
        objective="select source-traced API candidates",
        data_scope="sample",
        limit=3,
    )
    assert report["schema"] == "AOI_CapabilityTrustReport/v0.1"
    assert report["summary"]["candidate_count"] <= 3
    assert "quality guarantee" in " ".join(report["known_limits"])
    assert "security certification" in " ".join(report["not_asserted"])
