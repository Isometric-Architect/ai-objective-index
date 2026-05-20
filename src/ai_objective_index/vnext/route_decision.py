from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .evidence_summary import CapabilityEvidenceSummary
from .risk_boundary import CapabilityRiskBoundary


RouteDecisionLabel = Literal[
    "ALLOW_CANDIDATE",
    "ALLOW_WITH_LIMITS",
    "HOLD_EVIDENCE",
    "HOLD_MISSING_FIELDS",
    "HOLD_POLICY_CLARITY",
    "HOLD_SECURITY_REVIEW",
    "BLOCK_FORBIDDEN_ACTION",
    "BLOCK_UNSUPPORTED_CLAIM",
    "BLOCK_HIGH_RISK_DOMAIN",
    "BLOCK_NO_SOURCE_TRACE",
]


class CapabilityRouteDecision(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_CapabilityRouteDecision/v0.1", alias="schema")
    decision: RouteDecisionLabel
    reason: str
    claim_ceiling: str = "source-traced capability candidate; not verified"
    next_actions: list[str] = Field(default_factory=list)
    can_rank: bool = False
    can_compare: bool = False
    can_recommend_as_candidate: bool = False
    must_not_claim: list[str] = Field(
        default_factory=lambda: [
            "verified",
            "safe",
            "security certified",
            "quality guaranteed",
            "production-ready",
            "purchasing advice",
        ]
    )


CRITICAL_MISSING_FIELDS = {
    "pricing",
    "commercial_use_terms",
    "privacy_policy",
    "docs_url",
    "data_retention_policy",
}


def decide_route(
    evidence: CapabilityEvidenceSummary,
    risk_boundary: CapabilityRiskBoundary,
    missing_fields: list[str],
) -> CapabilityRouteDecision:
    if risk_boundary.forbidden_actions_detected:
        return CapabilityRouteDecision(
            decision="BLOCK_FORBIDDEN_ACTION",
            reason="Forbidden real-world action language was detected.",
            next_actions=["Remove forbidden action scope or keep the capability out of agent action paths."],
        )
    if risk_boundary.unsupported_claims_detected:
        return CapabilityRouteDecision(
            decision="BLOCK_UNSUPPORTED_CLAIM",
            reason="Unsupported verification, safety, certification, or quality claim was detected.",
            next_actions=["Rewrite public claims and keep the candidate below verification claim ceilings."],
        )
    if risk_boundary.security_claim_status == "HOLD_SECURITY_REVIEW_REQUIRED":
        return CapabilityRouteDecision(
            decision="HOLD_SECURITY_REVIEW",
            reason="Security-sensitive language or domain flags require review before stronger usage.",
            next_actions=["Run a separate security review before using this beyond source-traced comparison."],
            can_rank=True,
            can_compare=True,
        )
    if evidence.source_trace_count == 0:
        return CapabilityRouteDecision(
            decision="BLOCK_NO_SOURCE_TRACE",
            reason="No source trace is available for this capability candidate.",
            next_actions=["Add official source traces before ranking as a public beta candidate."],
        )
    critical_missing = sorted(CRITICAL_MISSING_FIELDS & set(missing_fields))
    if critical_missing:
        if {"commercial_use_terms", "privacy_policy", "data_retention_policy"} & set(critical_missing):
            return CapabilityRouteDecision(
                decision="HOLD_POLICY_CLARITY",
                reason=f"Policy clarity fields are missing: {', '.join(critical_missing[:5])}.",
                next_actions=["Collect official policy traces before stronger recommendations."],
                can_rank=True,
                can_compare=True,
            )
        return CapabilityRouteDecision(
            decision="HOLD_MISSING_FIELDS",
            reason=f"Critical fields are missing: {', '.join(critical_missing[:5])}.",
            next_actions=["Fill missing official docs/pricing fields before treating as a stronger candidate."],
            can_rank=True,
            can_compare=True,
        )
    if evidence.evidence_status in {"PARTIAL_TRACE", "STALE_OR_INCOMPLETE"}:
        return CapabilityRouteDecision(
            decision="HOLD_EVIDENCE",
            reason="Evidence is partial or stale/incomplete.",
            next_actions=["Add more source traces and rerun the trust report."],
            can_rank=True,
            can_compare=True,
        )
    return CapabilityRouteDecision(
        decision="ALLOW_WITH_LIMITS" if risk_boundary.hold_use else "ALLOW_CANDIDATE",
        reason="Source traces are present and no hard risk boundary blocked candidate routing.",
        next_actions=["Use only as a source-traced candidate; do not claim verification, safety, or quality."],
        can_rank=True,
        can_compare=True,
        can_recommend_as_candidate=True,
    )
