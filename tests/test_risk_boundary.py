from ai_objective_index.models import ActionObject, MissingField
from ai_objective_index.vnext.risk_boundary import assess_risk_boundary


def test_risk_boundary_blocks_positive_safety_claim_not_unverified_status():
    action_object = ActionObject(
        object_id="claimy",
        name="Claimy Tool",
        object_type="ToolObject",
        summary="This tool is security certified and quality guaranteed.",
        status="EXTRACTED_UNVERIFIED",
    )
    boundary = assess_risk_boundary(action_object, [])
    assert "security certified" in boundary.unsupported_claims_detected
    assert "quality guaranteed" in boundary.unsupported_claims_detected


def test_risk_boundary_unverified_word_is_not_blocked():
    action_object = ActionObject(
        object_id="plain",
        name="Plain Tool",
        object_type="ToolObject",
        summary="This is an unverified metadata candidate.",
        status="EXTRACTED_UNVERIFIED",
    )
    boundary = assess_risk_boundary(
        action_object,
        [MissingField(field="pricing", why_it_matters="", recommended_source="", severity="medium")],
    )
    assert "verified" not in boundary.unsupported_claims_detected
    assert boundary.product_claim_status == "HOLD_PRODUCT_EVIDENCE_REQUIRED"
