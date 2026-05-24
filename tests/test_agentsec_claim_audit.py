from ai_objective_index.agentsec_claim_audit import run_agentsec_claim_audit


def test_agentsec_claim_audit_passes_current_docs():
    result = run_agentsec_claim_audit(write_result=False)

    assert result["decision"] == "PASS_AGENTSEC_CLAIM_BOUNDARY"
    assert result["risky_phrase_count"] == 0
    assert result["external_actions_performed"] is False
