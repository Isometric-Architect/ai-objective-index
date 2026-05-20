from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CapabilityCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="aoi.vnext.capability_card.v0_3", alias="schema")
    capability_id: str
    provider: str
    name: str
    version: str | None = None
    integration: dict[str, Any] = Field(default_factory=dict)
    supported_objectives: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    permission_scope: list[str] = Field(default_factory=list)
    cost_model: dict[str, Any] = Field(default_factory=dict)
    latency_class: str = "unknown"
    context_burden: str = "unknown"
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    known_failures: list[dict[str, Any]] = Field(default_factory=list)
    allowed_use: list[str] = Field(default_factory=list)
    hold_use: list[str] = Field(default_factory=list)
    blocked_use: list[str] = Field(default_factory=list)
    security: dict[str, Any] = Field(default_factory=dict)
    maintenance: dict[str, Any] = Field(default_factory=dict)
