from ai_objective_index.agent_discovery_eval.test_residual_reconciliation import run_test_residual_reconciliation


def test_residual_reconciliation_classifies_without_false_full_suite_green():
    result = run_test_residual_reconciliation(write_result=True)

    assert result["decision"] == "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED"
    assert result["classification"] == "unrelated_generated_payload_state"
    assert result["package_regression"] is False
    assert result["full_suite_green_claim_allowed"] is False
    assert result["safe_to_stage_generated_leftovers"] is False
