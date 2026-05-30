from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentDiscoverRequest(BaseModel):
    schema_: str = Field(default="AOI_AgentDiscoverRequest/v0.1", alias="schema")
    objective: str
    query: str
    data_scope: str = "sample"
    desired_capability_type: str = "mcp_or_api"
    freshness_preference: str = "prefer_recent_source_traces_but_keep_hold_candidates_visible"


class AgentPreflightRequest(BaseModel):
    schema_: str = Field(default="AOI_AgentPreflightRequest/v0.1", alias="schema")
    candidate_id: str
    intended_use: str
    available_metadata: dict[str, Any] = Field(default_factory=dict)
    required_permissions: list[str] = Field(default_factory=list)
    organization_policy_optional: dict[str, Any] = Field(default_factory=dict)


class AgentAdoptionStatus(BaseModel):
    capability_card_present: bool
    discover_mode_available: bool
    preflight_mode_available: bool
    examples_present: bool
    private_kernel_exposed: Literal[False] = False
    external_action_authorization: Literal[False] = False
    pyPI_upload_performed: Literal[False] = False
    mcp_registry_publish_performed: Literal[False] = False
