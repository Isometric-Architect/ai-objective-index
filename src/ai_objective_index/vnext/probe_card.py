from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ProbeCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="aoi.vnext.probe_card.v0_3", alias="schema")
    probe_id: str
    target_capability: str
    objective_scope: str
    canary_input: dict[str, Any] = Field(default_factory=dict)
    expected_behavior: str
    negative_control: dict[str, Any] = Field(default_factory=dict)
    sandbox_policy: str = "local_or_read_only"
    pass_fail: Literal["pass", "fail", "hold", "not_run"] = "not_run"
    failure_type: str | None = None
    receipt_hash: str | None = None
