from ai_objective_index.source_governance import (
    PromotionDecision,
    SourceStatus,
    can_promote_field,
    classify_source_url,
    source_status_before_evidence,
)


def test_generated_sample_cannot_promote_to_verified() -> None:
    decision = can_promote_field(
        "pricing",
        SourceStatus.GENERATED,
        confidence=0.99,
        status="EXTRACTED_UNVERIFIED",
    )
    assert decision != PromotionDecision.ALLOW_INTERNAL_READOUT


def test_source_url_presence_alone_is_not_supported_claim() -> None:
    result = source_status_before_evidence(
        {
            "field": "pricing",
            "source_url": "https://example.com/pricing",
            "confidence": 0.1,
            "status": "UNVERIFIED",
        }
    )
    assert result["source_supported"] is False
    assert result["promotion_decision"] != "ALLOW_INTERNAL_READOUT"


def test_stale_requires_reconfirmation() -> None:
    decision = can_promote_field(
        "pricing",
        classify_source_url("https://vendor.test/pricing"),
        confidence=0.95,
        status="STALE",
    )
    assert decision == PromotionDecision.HOLD_RECONFIRMATION
