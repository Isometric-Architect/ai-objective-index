from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutionReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="aoi.vnext.execution_receipt.v0_3", alias="schema")
    receipt_id: str
    objective_id: str
    capability_id: str
    agent_id_hash: str
    environment_class: str
    selected_pipeline: list[str] = Field(default_factory=list)
    outcome: Literal["success", "partial", "fail", "hold", "blocked"]
    verifier_result: dict[str, Any] = Field(default_factory=dict)
    negative_control_result: dict[str, Any] = Field(default_factory=dict)
    latency_bucket: str = "unknown"
    cost_bucket: str = "unknown"
    error_type: str | None = None
    residual_found: bool = False
    claim_ceiling_change: str | None = None
    timestamp: datetime
