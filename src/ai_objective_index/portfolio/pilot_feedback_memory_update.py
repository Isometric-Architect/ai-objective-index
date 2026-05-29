from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .pilot_feedback_classifier import PilotFeedbackClassification
from .pilot_feedback_packet import PilotFeedbackPacket


UpdateType = Literal[
    "add_fixture_candidate",
    "add_negative_control_candidate",
    "update_claim_boundary",
    "request_more_evidence",
    "update_finding_explanation",
    "no_change",
]
MemoryStatus = Literal["pending", "accepted", "incorporated", "rejected", "closed"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PilotFeedbackMemoryUpdate(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotFeedbackMemoryUpdate/v0.1", alias="schema")
    update_id: str
    feedback_id: str
    dry_run_id: str
    generated_at: str = Field(default_factory=timestamp)
    vertical: str
    update_type: UpdateType
    memory_status: MemoryStatus = "pending"
    before_summary: str = ""
    after_summary: str = ""
    unresolved_questions: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    external_action_authorized: bool = False


def choose_update_type(classification: PilotFeedbackClassification) -> UpdateType:
    if classification.should_add_negative_control:
        return "add_negative_control_candidate"
    if classification.should_add_fixture:
        return "add_fixture_candidate"
    if classification.should_update_claim_boundary:
        return "update_claim_boundary"
    if classification.should_request_evidence:
        return "request_more_evidence"
    if classification.should_update_finding:
        return "update_finding_explanation"
    return "no_change"


def build_feedback_memory_update(
    packet: PilotFeedbackPacket,
    classification: PilotFeedbackClassification,
) -> PilotFeedbackMemoryUpdate:
    update_type = choose_update_type(classification)
    unresolved: list[str] = []
    if classification.classification.startswith("HOLD_"):
        unresolved.append("more local context or owner confirmation is required before a second local pass")
    if classification.classification.startswith("BLOCK_"):
        unresolved.append("blocked feedback must be rewritten without forbidden action, secret/private data, or certification request")
    return PilotFeedbackMemoryUpdate(
        update_id=f"feedback-memory-update-{packet.feedback_id}",
        feedback_id=packet.feedback_id,
        dry_run_id=packet.dry_run_id,
        vertical=packet.vertical,
        update_type=update_type,
        memory_status="pending" if not classification.classification.startswith("BLOCK_") else "rejected",
        before_summary="ROE-13 feedback memory has a pending dry-run entry for the vertical.",
        after_summary=f"ROE-14 records feedback as {classification.classification} with update_type={update_type}.",
        unresolved_questions=unresolved,
        next_actions=classification.next_actions,
    )


def memory_update_to_jsonable(update: PilotFeedbackMemoryUpdate) -> dict[str, Any]:
    return update.model_dump(mode="json", by_alias=True)
