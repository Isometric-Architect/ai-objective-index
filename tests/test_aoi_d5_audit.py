from ai_objective_index.agent_adoption.cdp_audit import run_cdp_audit


def test_aoi_d5_audit_passes_or_holds_without_false_green_claim():
    result = run_cdp_audit(write_result=True)

    assert result["decision"] in {
        "PASS_CAPABILITY_DECISION_PACKET_READY",
        "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED",
    }
    assert result["capability_decision_packet_valid"] is True
    assert result["route_semantics_count"] >= 25
    assert result["reason_code_count"] >= 20
    assert result["no_false_full_suite_green_claim"] is True
