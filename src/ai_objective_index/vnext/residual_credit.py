from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResidualCredit(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="aoi.vnext.residual_credit.v0_3", alias="schema")
    capability_id: str
    objective_scope: str
    raw_success_score: float = Field(ge=0, le=1)
    eco_success_score: float = Field(ge=0, le=1)
    negative_control_score: float = Field(ge=0, le=1)
    security_risk: float = Field(ge=0, le=1)
    context_burden: float = Field(ge=0, le=1)
    integration_reliability: float = Field(ge=0, le=1)
    known_failure_similarity: float = Field(ge=0, le=1)
    freshness: float = Field(ge=0, le=1)
    allowed_use: list[str] = Field(default_factory=list)
    hold_use: list[str] = Field(default_factory=list)
    blocked_use: list[str] = Field(default_factory=list)
    residual_notes: list[str] = Field(default_factory=list)
