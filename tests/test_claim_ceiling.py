from ai_objective_index.claim_ceiling import (
    ClaimCeiling,
    claim_ceiling_not_asserted_list,
    enforce_claim_ceiling,
    infer_claim_ceiling,
)
from ai_objective_index.models import ActionObject


def test_extracted_unverified_maps_to_ceiling() -> None:
    action_object = ActionObject(
        object_id="ceiling-object",
        name="Ceiling Object",
        object_type="ToolObject",
        summary="Fixture object for claim ceiling checks.",
        status="EXTRACTED_UNVERIFIED",
        confidence=0.5,
    )
    assert infer_claim_ceiling(action_object) == ClaimCeiling.EXTRACTED_UNVERIFIED


def test_score_does_not_become_quality_guarantee() -> None:
    payload = enforce_claim_ceiling({"objective_score": 92.0, "claim_ceiling": "SOURCE_TRACED_READOUT"})
    assert "not a quality guarantee" in payload["not_asserted"]
    assert "not permission to buy, book, pay, log in, submit forms, email, connect accounts, purchase, or sign contracts" in payload["not_asserted"]


def test_claim_ceiling_not_asserted_has_supplier_guard() -> None:
    not_asserted = claim_ceiling_not_asserted_list(ClaimCeiling.EXTRACTED_UNVERIFIED)
    assert "not supplier-verified data" in not_asserted
