from ai_objective_index.agentsec.models import AgentSecActionBoundaryReceipt, PermissionScope, ToolRiskPacket


def test_agentsec_tool_risk_packet_serializes():
    packet = ToolRiskPacket(
        packet_id="agentsec-risk-test",
        tool_id="fixture.local/tool",
        name="Fixture Tool",
        metadata_hash="abc123",
        permission_scope=PermissionScope(network_access=False),
        risk_decision="ALLOW_METADATA_ONLY",
    )

    payload = packet.model_dump(mode="json", by_alias=True)

    assert payload["schema"] == "AgentSec_ToolRiskPacket/v0.1"
    assert payload["risk_decision"] == "ALLOW_METADATA_ONLY"
    assert "security certification" in " ".join(payload["must_not_claim"])


def test_agentsec_action_boundary_receipt_never_certifies():
    receipt = AgentSecActionBoundaryReceipt(
        receipt_id="agentsec-receipt-test",
        packet_id="agentsec-risk-test",
        decision="HOLD_REVIEW_REQUIRED",
    )

    assert receipt.can_certify_security is False
    assert receipt.can_certify_quality is False
    assert receipt.can_authorize_action is False
