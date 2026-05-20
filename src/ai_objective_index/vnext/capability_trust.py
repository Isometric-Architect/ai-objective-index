from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .evidence_summary import CapabilityEvidenceSummary
from .risk_boundary import CapabilityRiskBoundary
from .route_decision import CapabilityRouteDecision


IntegrationType = Literal[
    "api",
    "mcp_server",
    "python_package",
    "dataset",
    "service",
    "tool",
    "agent",
    "unknown",
]


class ObjectiveCapabilityMatch(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ObjectiveCapabilityMatch/v0.1", alias="schema")
    objective_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    domain_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    constraint_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    integration_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    policy_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_fit: float = Field(default=0.0, ge=0.0, le=1.0)
    missing_field_penalty: float = Field(default=0.0, ge=0.0, le=1.0)
    forbidden_action_penalty: float = Field(default=0.0, ge=0.0, le=1.0)
    unsupported_claim_penalty: float = Field(default=0.0, ge=0.0, le=1.0)
    explanation: list[str] = Field(default_factory=list)


class CapabilityTrustProfile(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_CapabilityTrustProfile/v0.1", alias="schema")
    profile_id: str = "demo_profile_v0_1"
    objective_fit: float = 0.14
    source_trace_coverage: float = 0.14
    evidence_quality: float = 0.12
    integration_readiness: float = 0.1
    policy_clarity: float = 0.1
    documentation_clarity: float = 0.1
    freshness: float = 0.08
    missing_field_penalty: float = 0.1
    residual_risk_penalty: float = 0.08
    unsupported_claim_penalty: float = 0.08
    forbidden_action_penalty: float = 0.12
    limitations: list[str] = Field(
        default_factory=lambda: [
            "Demo weights are not objective truth.",
            "This profile is not an anti-gaming or security signal.",
            "ALLOW labels do not mean verified, safe, certified, or quality guaranteed.",
        ]
    )


class CapabilityTrustCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_CapabilityTrustCard/v0.1", alias="schema")
    trust_card_id: str
    objective_id: str
    capability_id: str
    object_id: str | None = None
    name: str
    provider: str | None = None
    domain: str
    integration_type: IntegrationType = "unknown"
    status: str
    source_trace_ids: list[str] = Field(default_factory=list)
    evidence_summary: CapabilityEvidenceSummary
    match: ObjectiveCapabilityMatch
    risk_boundary: CapabilityRiskBoundary
    route_decision: CapabilityRouteDecision
    score_components: dict[str, Any] = Field(default_factory=dict)
    residual_notes: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    known_limits: list[str] = Field(default_factory=list)
    generated_at: str


def compute_demo_trust_score(
    match: ObjectiveCapabilityMatch,
    evidence_summary: CapabilityEvidenceSummary,
    risk_boundary: CapabilityRiskBoundary,
    profile: CapabilityTrustProfile | None = None,
) -> dict[str, float | str]:
    profile = profile or CapabilityTrustProfile()
    raw = (
        match.objective_fit * profile.objective_fit
        + evidence_summary.source_trace_coverage * profile.source_trace_coverage
        + evidence_summary.confidence * profile.evidence_quality
        + match.integration_fit * profile.integration_readiness
        + match.policy_fit * profile.policy_clarity
        + match.evidence_fit * profile.documentation_clarity
        + match.constraint_fit * profile.freshness
    )
    penalty = (
        match.missing_field_penalty * profile.missing_field_penalty
        + (0.5 if risk_boundary.risk_level == "medium" else 1.0 if risk_boundary.risk_level == "high" else 0.0)
        * profile.residual_risk_penalty
        + match.unsupported_claim_penalty * profile.unsupported_claim_penalty
        + match.forbidden_action_penalty * profile.forbidden_action_penalty
    )
    return {
        "profile_id": profile.profile_id,
        "demo_trust_score": round(max(0.0, min(1.0, raw - penalty)), 3),
        "raw_component_sum": round(raw, 3),
        "penalty_sum": round(penalty, 3),
    }
