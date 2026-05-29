from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


FeedbackStatus = Literal["pending", "received", "incorporated", "closed"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PilotIntakeFeedbackMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotIntakeFeedbackMemory/v0.1", alias="schema")
    intake_id: str
    route_id: str
    generated_at: str = Field(default_factory=timestamp)
    feedback_status: FeedbackStatus = "pending"
    issue_categories: list[str] = Field(default_factory=list)
    follow_up_actions: list[str] = Field(default_factory=list)
    should_request_more_consent: bool = False
    should_request_redacted_artifact: bool = False
    should_change_vertical_route: bool = False
    should_add_negative_control: bool = False
    should_add_fixture: bool = False
    should_update_claim_boundary: bool = False
    timestamp: str = Field(default_factory=timestamp)


def build_feedback_memory_entry(route: dict[str, Any]) -> PilotIntakeFeedbackMemory:
    blockers = route.get("blockers", [])
    selected = route.get("selected_vertical", "hold_manual_triage")
    return PilotIntakeFeedbackMemory(
        intake_id=route.get("intake_id", "unknown"),
        route_id=route.get("route_id", "unknown"),
        issue_categories=blockers or ["sample_intake_ready"],
        follow_up_actions=[
            "request owner-confirmed local artifact when moving beyond sample intake",
            "rerun redaction preflight before packaging a pilot receipt",
            "keep output claim-bounded and local/offline",
        ],
        should_request_more_consent=selected == "block_insufficient_consent",
        should_request_redacted_artifact="raw_private_data_declared" in blockers,
        should_change_vertical_route=selected == "hold_manual_triage",
        should_add_negative_control=False,
        should_add_fixture=True,
        should_update_claim_boundary=False,
    )


def feedback_memory_to_jsonable(memory: PilotIntakeFeedbackMemory) -> dict[str, Any]:
    return memory.model_dump(mode="json", by_alias=True)
