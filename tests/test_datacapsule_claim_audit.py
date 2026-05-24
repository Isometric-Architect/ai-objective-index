from ai_objective_index.datacapsule_claim_audit import run_datacapsule_claim_audit


def test_datacapsule_claim_audit_passes_current_docs():
    result = run_datacapsule_claim_audit(write_result=False)

    assert result["decision"] == "PASS_DATACAPSULE_CLAIM_BOUNDARY"
    assert result["risky_phrase_count"] == 0
    assert result["crawler_used"] is False
    assert result["token_printed"] is False
