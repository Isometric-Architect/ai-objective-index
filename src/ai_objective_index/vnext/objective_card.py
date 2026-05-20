from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ObjectiveCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="aoi.vnext.objective_card.v0_3", alias="schema")
    objective_id: str
    task: str
    domain: str
    agent_role: str
    desired_output: str
    risk_level: Literal["low", "medium", "high", "critical"] = "medium"
    budget: dict[str, Any] = Field(default_factory=dict)
    latency: dict[str, Any] = Field(default_factory=dict)
    environment: dict[str, Any] = Field(default_factory=dict)
    allowed_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    evidence_requirement: str = "source_trace_required"
    claim_ceiling: str = "source-traced capability candidate; not verified"
