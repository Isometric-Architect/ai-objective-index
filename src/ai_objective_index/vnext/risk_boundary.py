from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.models import ActionObject, MissingField


RiskLevel = Literal["low", "medium", "high", "unknown"]
SecurityClaimStatus = Literal[
    "NOT_ASSESSED",
    "SOURCE_TRACED_ONLY",
    "HOLD_SECURITY_REVIEW_REQUIRED",
    "BLOCK_SECURITY_CLAIM",
]
LegalClaimStatus = Literal["NOT_ASSESSED", "HOLD_LEGAL_REVIEW_REQUIRED", "BLOCK_LEGAL_CLAIM"]
ProductClaimStatus = Literal[
    "NOT_ASSESSED",
    "HOLD_PRODUCT_EVIDENCE_REQUIRED",
    "BLOCK_PRODUCT_READY_CLAIM",
]

FORBIDDEN_ACTIONS = {
    "payment",
    "booking",
    "login",
    "email",
    "email sending",
    "form submission",
    "purchase",
    "contract",
    "contract signing",
    "account connection",
    "supplier claim",
    "supplier verification",
}

UNSUPPORTED_CLAIMS = {
    "verified",
    "safe",
    "security certified",
    "quality guaranteed",
    "production-ready",
    "official standard",
    "best tool guaranteed",
    "trusted by all agents",
}


class CapabilityRiskBoundary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_CapabilityRiskBoundary/v0.1", alias="schema")
    risk_level: RiskLevel = "unknown"
    allowed_use: list[str] = Field(default_factory=list)
    hold_use: list[str] = Field(default_factory=list)
    blocked_use: list[str] = Field(default_factory=list)
    forbidden_actions_detected: list[str] = Field(default_factory=list)
    unsupported_claims_detected: list[str] = Field(default_factory=list)
    sensitive_domain_flags: list[str] = Field(default_factory=list)
    security_claim_status: SecurityClaimStatus = "NOT_ASSESSED"
    legal_claim_status: LegalClaimStatus = "NOT_ASSESSED"
    product_claim_status: ProductClaimStatus = "NOT_ASSESSED"
    route_block_reasons: list[str] = Field(default_factory=list)


def _haystack(action_object: ActionObject) -> str:
    parts = [
        action_object.name,
        action_object.summary,
        " ".join(action_object.capabilities),
        " ".join(action_object.categories),
        str(action_object.docs or {}),
        str(action_object.policies or {}),
        str(getattr(action_object, "display_status", "")),
    ]
    return " ".join(part for part in parts if part).lower()


def assess_risk_boundary(
    action_object: ActionObject,
    missing_fields: list[MissingField] | None = None,
) -> CapabilityRiskBoundary:
    text = _haystack(action_object)
    missing_names = {item.field for item in (missing_fields or [])}
    forbidden = sorted(action for action in FORBIDDEN_ACTIONS if re.search(rf"\b{re.escape(action)}\b", text))
    unsupported = sorted(claim for claim in UNSUPPORTED_CLAIMS if re.search(rf"\b{re.escape(claim)}\b", text))
    sensitive: list[str] = []
    for marker in ("medical", "legal", "financial", "security", "procurement"):
        if marker in text:
            sensitive.append(marker)

    blocked: list[str] = []
    hold: list[str] = []
    allowed = [
        "read-only objective-relative comparison",
        "source-traced candidate ranking",
        "missing-field review",
    ]
    if forbidden:
        blocked.append("Forbidden action language detected.")
    if unsupported:
        blocked.append("Unsupported verification/safety/quality claim detected.")
    if {"privacy_policy", "data_retention_policy"} & missing_names:
        hold.append("Data handling policy evidence needs review.")
    if "commercial_use_terms" in missing_names:
        hold.append("Commercial-use policy clarity needs review.")
    if sensitive:
        hold.append("Sensitive-domain language requires human review before stronger claims.")

    security_status: SecurityClaimStatus = "NOT_ASSESSED"
    if "security certified" in unsupported or "safe" in unsupported:
        security_status = "BLOCK_SECURITY_CLAIM"
    elif "security" in sensitive:
        security_status = "HOLD_SECURITY_REVIEW_REQUIRED"

    legal_status: LegalClaimStatus = "NOT_ASSESSED"
    if "legal advice" in text:
        legal_status = "BLOCK_LEGAL_CLAIM"
    elif "legal" in sensitive:
        legal_status = "HOLD_LEGAL_REVIEW_REQUIRED"

    product_status: ProductClaimStatus = "NOT_ASSESSED"
    if "production-ready" in unsupported or "quality guaranteed" in unsupported:
        product_status = "BLOCK_PRODUCT_READY_CLAIM"
    elif "pricing" in missing_names or "docs_url" in missing_names:
        product_status = "HOLD_PRODUCT_EVIDENCE_REQUIRED"

    risk_level: RiskLevel
    if forbidden or unsupported:
        risk_level = "high"
    elif sensitive or hold:
        risk_level = "medium"
    elif missing_names:
        risk_level = "low"
    else:
        risk_level = "unknown"

    return CapabilityRiskBoundary(
        risk_level=risk_level,
        allowed_use=allowed,
        hold_use=hold,
        blocked_use=blocked,
        forbidden_actions_detected=forbidden,
        unsupported_claims_detected=unsupported,
        sensitive_domain_flags=sensitive,
        security_claim_status=security_status,
        legal_claim_status=legal_status,
        product_claim_status=product_status,
        route_block_reasons=blocked,
    )
