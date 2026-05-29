from ai_objective_index.portfolio.qira_ci_evidence_summary import build_ci_evidence_summary


def test_qira_ci_evidence_missing_creates_hold_shape():
    summary = build_ci_evidence_summary("task-1", source_type="generated_sample")

    assert summary.evidence_status == "PARTIAL_CI_EVIDENCE"
    assert "independent_ci_run" in summary.missing_evidence
    assert "security_certified" in summary.must_not_claim
