from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .feedback_reply_classifier import FeedbackReplyClassification
from .feedback_reply_packet import FeedbackReplyPacket
from .feedback_reply_router import FeedbackReplyRoute


TriageStatus = Literal["pending", "routed", "blocked", "hold"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class FeedbackReplyTriageEntry(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackReplyTriage/v0.1", alias="schema")
    triage_id: str
    reply_id: str
    classification_id: str
    route_id: str
    generated_at: str = Field(default_factory=timestamp)
    triage_label: str
    severity: str
    owner_followup_needed: bool = False
    evidence_needed: list[str] = Field(default_factory=list)
    second_run_candidate: bool = False
    memory_candidate: bool = False
    next_action: str = ""
    status: TriageStatus = "pending"


def build_triage_entry(
    packet: FeedbackReplyPacket,
    classification: FeedbackReplyClassification,
    route: FeedbackReplyRoute,
) -> FeedbackReplyTriageEntry:
    if classification.classification.startswith("BLOCK_") or route.selected_vertical == "block":
        status: TriageStatus = "blocked"
    elif classification.classification.startswith("HOLD_") or route.selected_vertical == "hold_manual_triage":
        status = "hold"
    else:
        status = "routed"
    return FeedbackReplyTriageEntry(
        triage_id=f"triage-{packet.reply_id}",
        reply_id=packet.reply_id,
        classification_id=classification.classification_id,
        route_id=route.route_id,
        triage_label=f"{route.selected_vertical}:{classification.classification}",
        severity=classification.severity,
        owner_followup_needed=classification.classification in {"HOLD_CONSENT_UNCLEAR", "HOLD_NEEDS_MORE_CONTEXT"},
        evidence_needed=route.required_next_artifacts,
        second_run_candidate=route.can_create_second_run_candidate,
        memory_candidate=route.can_create_memory_candidate,
        next_action=classification.next_actions[-1] if classification.next_actions else "review locally",
        status=status,
    )


def triage_to_jsonable(entry: FeedbackReplyTriageEntry) -> dict[str, Any]:
    return entry.model_dump(mode="json", by_alias=True)
