from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


VNextDataScope = Literal["sample", "integrated", "mcp_registry", "public_beta_mcp"]
RiskTolerance = Literal["low", "medium", "high", "unknown"]


class ObjectiveRouteConstraints(BaseModel):
    model_config = ConfigDict(extra="allow")

    require_source_trace: bool = True
    require_policy_clarity: bool = False
    require_docs: bool = False
    require_pricing: bool = False
    require_license: bool = False
    require_repository: bool = False
    allowed_integration_types: list[str] | None = None
    forbidden_actions: list[str] | None = None
    risk_tolerance: RiskTolerance = "unknown"


class ObjectiveRouteInclude(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_traces: bool = True
    missing_fields: bool = True
    score_components: bool = True
    known_limits: bool = True


class ObjectiveRouteRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    query: str
    objective: str
    domain: str = "mcp_servers"
    data_scope: VNextDataScope = "sample"
    limit: int = Field(default=10, ge=1, le=100)
    constraints: ObjectiveRouteConstraints = Field(default_factory=ObjectiveRouteConstraints)
    include: ObjectiveRouteInclude = Field(default_factory=ObjectiveRouteInclude)


class ObjectiveRouteSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    total_candidates: int = 0
    allow_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    top_decision_reasons: list[dict[str, Any]] = Field(default_factory=list)
    claim_ceiling: str = "source-traced capability candidate; not verified; not security certified; not a quality guarantee"


class ObjectiveRouteResponse(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ObjectiveRouteResponse/v0.1", alias="schema")
    query: str
    objective: str
    domain: str
    data_scope: str
    generated_at: str
    route_summary: ObjectiveRouteSummary
    results: list[dict[str, Any]]
    known_limits: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(
        default_factory=lambda: [
            "verified",
            "safe",
            "security certified",
            "quality guaranteed",
            "production ready",
            "legal advice",
            "financial advice",
            "medical advice",
            "purchasing advice",
        ]
    )
    next_actions: list[str] = Field(default_factory=list)
    read_only: bool = True
    probe_execution: bool = False
    gateway_execution: bool = False
    external_fetch: bool = False
    pypi_upload_performed: bool = False
    mcp_registry_submission_performed: bool = False
    community_post_performed: bool = False
