from ai_objective_index.release_claim_audit import run_release_claim_audit, save_release_claim_audit


def test_release_claim_audit_runs_and_allows_forbidden_examples():
    result = run_release_claim_audit()

    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert "findings" in result
    assert "suggested_rewrites" in result
    assert result["actual_publish_performed"] is False
    assert result["live_network_used"] is False

    path = save_release_claim_audit(result)
    assert path.exists()
