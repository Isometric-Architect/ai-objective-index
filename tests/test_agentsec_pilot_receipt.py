from ai_objective_index.portfolio.agentsec_pilot_packager import build_receipt_from_policy_gate
from ai_objective_index.agentsec.policy_gate import SAMPLE_MANIFEST_SET, build_policy_gate_result


def test_agentsec_pilot_receipt_serializes():
    policy_gate = build_policy_gate_result(SAMPLE_MANIFEST_SET).model_dump(mode="json", by_alias=True)
    receipt = build_receipt_from_policy_gate(policy_gate)
    payload = receipt.model_dump(mode="json", by_alias=True)

    assert payload["schema"] == "ResidualOps_AgentSecPilotReceipt/v0.1"
    assert payload["review_scope"]["live_mcp_call"] is False
    assert payload["claim_boundary"]["not_security_certification"] is True
    assert payload["decision_summary"]["hold_count"] >= 1
    assert payload["external_actions_performed"] is False
