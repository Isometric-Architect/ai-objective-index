from ai_objective_index.qira_claim_audit import run_qira_claim_audit


def test_qira_claim_audit_passes_generated_docs_and_outputs():
    result = run_qira_claim_audit(write_result=True)

    assert result["decision"] == "PASS_QIRA_CLAIM_BOUNDARY"
    assert result["risky_phrase_count"] == 0
    assert result["external_actions_performed"] is False
