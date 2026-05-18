from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchResponse(BaseModel):
    read_only: bool = True
    data_scope: str = "sample"
    query: str
    objective: str | None = None
    results: list[dict[str, Any]]
    limitations: list[str]
    warnings: list[str] = Field(default_factory=list)
    forbidden_actions: list[str]
    action_boundary: dict[str, Any] = Field(default_factory=dict)


class RankOption(BaseModel):
    name: str
    url: str | None = None
    description: str | None = None


class RankOptionsRequest(BaseModel):
    options: list[RankOption]
    objective: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    scoring_profile: str = "default"
    data_scope: str = "sample"


class CompareRequest(BaseModel):
    object_ids: list[str]
    compare_fields: list[str] | None = None
    query: str | None = None
    objective: str | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    data_scope: str = "sample"


class DecisionReceiptRequest(BaseModel):
    query: str
    selected_object_id: str
    alternatives: list[str] = Field(default_factory=list)
    objective: str | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    data_scope: str = "sample"


class ErrorResponse(BaseModel):
    error: str
    object_id: str | None = None
    message: str
