from ai_objective_index.portfolio.feedback_second_run_executor import run_feedback_second_run_bridge


def test_feedback_second_run_readout_includes_claim_boundary():
    result = run_feedback_second_run_bridge(sample=True, write_result=False)
    readout = result["readout"]
    assert "Claim Boundaries" in readout
    assert "not security certification" in readout.lower()
    assert "Skipped Candidates" in readout
