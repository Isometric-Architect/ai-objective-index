from __future__ import annotations

from enum import Enum
from typing import Any


class SourceStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    OFFICIAL = "OFFICIAL"
    OFFICIAL_DOCS = "OFFICIAL_DOCS"
    OFFICIAL_PRICING = "OFFICIAL_PRICING"
    OFFICIAL_TERMS = "OFFICIAL_TERMS"
    OFFICIAL_GITHUB = "OFFICIAL_GITHUB"
    THIRD_PARTY_REVIEW = "THIRD_PARTY_REVIEW"
    COMMUNITY = "COMMUNITY"
    GENERATED = "GENERATED"
    SAMPLE = "SAMPLE"
    STALE = "STALE"
    UNVERIFIED = "UNVERIFIED"


class PromotionDecision(str, Enum):
    ALLOW_INTERNAL_READOUT = "ALLOW_INTERNAL_READOUT"
    HOLD_SOURCE = "HOLD_SOURCE"
    HOLD_VALIDATOR = "HOLD_VALIDATOR"
    HOLD_RECONFIRMATION = "HOLD_RECONFIRMATION"
    BLOCK_FORBIDDEN_PROMOTION = "BLOCK_FORBIDDEN_PROMOTION"


_GENERATED_OR_SAMPLE_STATUSES = {
    "DISCOVERED",
    "EXTRACTED",
    "UNVERIFIED",
    "EXTRACTED_UNVERIFIED",
    "NEEDS_REVIEW",
}


def _text(value: Any) -> str:
    return str(value or "").strip().lower()


def classify_source_url(url: str | None, source_title: str | None = None) -> SourceStatus:
    """Classify a source before treating it as evidence.

    This is intentionally conservative and URL/title-based only. It does not
    fetch pages or verify ownership.
    """

    if not url:
        return SourceStatus.UNKNOWN

    haystack = f"{_text(url)} {_text(source_title)}"
    if "fixture" in haystack or "generated" in haystack:
        return SourceStatus.GENERATED
    if "sample" in haystack or "example.com" in haystack:
        return SourceStatus.SAMPLE
    if "github.com" in haystack:
        return SourceStatus.OFFICIAL_GITHUB
    if any(token in haystack for token in ("terms", "privacy", "legal", "policy")):
        return SourceStatus.OFFICIAL_TERMS
    if any(token in haystack for token in ("pricing", "plans", "billing")):
        return SourceStatus.OFFICIAL_PRICING
    if any(token in haystack for token in ("docs", "documentation", "api-reference", "reference", "quickstart")):
        return SourceStatus.OFFICIAL_DOCS
    if any(token in haystack for token in ("review", "blog", "directory")):
        return SourceStatus.THIRD_PARTY_REVIEW
    if any(token in haystack for token in ("forum", "community", "reddit", "discord")):
        return SourceStatus.COMMUNITY
    return SourceStatus.OFFICIAL


def can_promote_field(
    field_name: str,
    source_status: SourceStatus | str,
    confidence: float,
    status: str | None,
) -> PromotionDecision:
    """Return whether a field can be promoted beyond internal readout."""

    source_value = source_status.value if isinstance(source_status, SourceStatus) else str(source_status)
    status_value = str(status or "").upper()
    field = field_name.lower()

    if status_value == "BLOCKED":
        return PromotionDecision.BLOCK_FORBIDDEN_PROMOTION
    if source_value == SourceStatus.STALE.value or status_value == "STALE":
        return PromotionDecision.HOLD_RECONFIRMATION
    if status_value in _GENERATED_OR_SAMPLE_STATUSES:
        return PromotionDecision.HOLD_VALIDATOR
    if source_value in {
        SourceStatus.UNKNOWN.value,
        SourceStatus.GENERATED.value,
        SourceStatus.SAMPLE.value,
        SourceStatus.UNVERIFIED.value,
        SourceStatus.COMMUNITY.value,
    }:
        return PromotionDecision.HOLD_SOURCE
    if confidence < 0.5:
        return PromotionDecision.HOLD_SOURCE
    if any(token in field for token in ("pricing", "price", "free_plan", "rate_limit")):
        if source_value != SourceStatus.OFFICIAL_PRICING.value and confidence < 0.9:
            return PromotionDecision.HOLD_SOURCE
    if any(token in field for token in ("policy", "terms", "privacy", "commercial", "license", "retention")):
        allowed_sources = {
            SourceStatus.OFFICIAL_TERMS.value,
            SourceStatus.OFFICIAL_DOCS.value,
            SourceStatus.OFFICIAL_PRICING.value,
            SourceStatus.OFFICIAL_GITHUB.value,
        }
        if source_value not in allowed_sources or confidence < 0.7:
            return PromotionDecision.HOLD_SOURCE
    return PromotionDecision.ALLOW_INTERNAL_READOUT


def source_status_before_evidence(field_claim: dict[str, Any]) -> dict[str, Any]:
    """Attach source status and promotion decision to a field claim."""

    source_status = classify_source_url(
        field_claim.get("source_url"),
        source_title=field_claim.get("source_title"),
    )
    confidence = float(field_claim.get("confidence", 0.0) or 0.0)
    decision = can_promote_field(
        str(field_claim.get("field") or ""),
        source_status,
        confidence,
        field_claim.get("status"),
    )
    return {
        "field": field_claim.get("field"),
        "source_status": source_status.value,
        "promotion_decision": decision.value,
        "source_supported": decision == PromotionDecision.ALLOW_INTERNAL_READOUT,
        "warning": "Source URL presence alone is not a supported claim."
        if decision != PromotionDecision.ALLOW_INTERNAL_READOUT
        else None,
    }
