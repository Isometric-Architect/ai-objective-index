from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ObjectStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    EXTRACTED = "EXTRACTED"
    CANDIDATE = "CANDIDATE"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    STALE = "STALE"
    BLOCKED = "BLOCKED"
    EXTRACTED_UNVERIFIED = "EXTRACTED_UNVERIFIED"
    CLAIMED = "CLAIMED"
    ACTION_READY = "ACTION_READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ObjectType(str, Enum):
    ToolObject = "ToolObject"
    APIObject = "APIObject"
    SaaSObject = "SaaSObject"
    MCPServer = "MCPServer"
    DatasetObject = "DatasetObject"
    ServiceObject = "ServiceObject"


class SourceRank(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    UNKNOWN = "UNKNOWN"


class ActionObject(BaseModel):
    """A rankable AOI object.

    The model intentionally allows extra fields because Package 0 sample data
    is richer than the Package 1 core fields.
    """

    model_config = ConfigDict(extra="allow")

    object_id: str
    name: str
    object_type: ObjectType | str
    summary: str = ""
    official_url: str | None = None
    source_urls: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    pricing: dict[str, Any] | None = Field(default_factory=dict)
    policies: dict[str, Any] | None = Field(default_factory=dict)
    docs: dict[str, Any] | None = Field(default_factory=dict)
    status: ObjectStatus | str = ObjectStatus.EXTRACTED_UNVERIFIED
    confidence: float = Field(default=0.5, ge=0, le=1)
    missing_fields: list[str] = Field(default_factory=list)
    last_checked_at: datetime | str | None = None
    source_rank: SourceRank | str = SourceRank.UNKNOWN

    @field_validator("capabilities", "categories", "source_urls", "missing_fields", mode="before")
    @classmethod
    def _list_or_empty(cls, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @field_validator("pricing", "policies", "docs", mode="before")
    @classmethod
    def _dict_or_empty(cls, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        return {"value": value}


class SourceTrace(BaseModel):
    model_config = ConfigDict(extra="allow")

    trace_id: str
    object_id: str
    field: str
    source_url: str
    source_title: str
    source_snippet: str
    retrieved_at: datetime | str
    confidence: float = Field(ge=0, le=1)
    source_rank: SourceRank | str = SourceRank.UNKNOWN


class ObjectiveScore(BaseModel):
    model_config = ConfigDict(extra="allow")

    object_id: str
    objective_score: float = Field(ge=0, le=100)
    score_components: dict[str, float]
    penalties: dict[str, float]
    rank_reason: list[str]
    warnings: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    status: ObjectStatus | str
    claim_ceiling: str | None = None
    obstructions: list[dict[str, Any]] = Field(default_factory=list)
    not_asserted: list[str] = Field(default_factory=list)


class MissingField(BaseModel):
    model_config = ConfigDict(extra="allow")

    field: str
    why_it_matters: str
    recommended_source: str
    severity: Literal["low", "medium", "high"]


class CompareResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    comparison_table: list[dict[str, Any]]
    best_for: list[str]
    missing_fields_summary: dict[str, list[str]]
    warnings: list[str] = Field(default_factory=list)
    score_summary: list[dict[str, Any]]


class DecisionReceipt(BaseModel):
    model_config = ConfigDict(extra="allow")

    selected_object_id: str
    selected_name: str
    objective: str | dict[str, Any] | None = None
    constraints_checked: list[dict[str, Any]]
    why_selected: list[str] | str
    alternatives: list[dict[str, Any]]
    known_limits: list[str]
    source_trace_ids: list[str]
    timestamp: datetime
    use_rights: dict[str, Any] = Field(default_factory=dict)
    claim_ceiling: str | None = None
    action_boundary: dict[str, Any] = Field(default_factory=dict)
    obstructions: list[dict[str, Any]] = Field(default_factory=list)
    not_asserted: list[str] = Field(default_factory=list)


class ObstructionCertificate(BaseModel):
    model_config = ConfigDict(extra="allow")

    object_id: str
    token: str
    reason: str
    missing_evidence: list[str] = Field(default_factory=list)
    next_action: str
    severity: Literal["low", "medium", "high", "block"]
    source_trace_ids: list[str] = Field(default_factory=list)
