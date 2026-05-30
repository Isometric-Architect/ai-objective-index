from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .feedback_reply_classifier import FeedbackReplyClassification
from .feedback_reply_packet import FeedbackReplyPacket
from .feedback_reply_router import FeedbackReplyRoute


MemoryStatus = Literal["pending_review", "accepted", "rejected"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class FeedbackReplyMemoryCandidate(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackReplyMemoryCandidate/v0.1", alias="schema")
    memory_candidate_id: str
    reply_id: str
    generated_at: str = Field(default_factory=timestamp)
    vertical: str
    issue_categories: list[str] = Field(default_factory=list)
    suggested_memory_update: str = ""
    suggested_fixture_candidate: str = ""
    suggested_negative_control_candidate: str = ""
    suggested_claim_boundary_update: str = ""
    status: MemoryStatus = "pending_review"
    must_not_claim: list[str] = Field(default_factory=list)


def build_memory_candidate(
    packet: FeedbackReplyPacket,
    classification: FeedbackReplyClassification,
    route: FeedbackReplyRoute,
) -> FeedbackReplyMemoryCandidate:
    accepted = route.can_create_memory_candidate
    return FeedbackReplyMemoryCandidate(
        memory_candidate_id=f"memory-candidate-{packet.reply_id}",
        reply_id=packet.reply_id,
        vertical=route.selected_vertical,
        issue_categories=classification.issue_categories,
        suggested_memory_update="record reply as local feedback memory candidate" if accepted else "do not add blocked reply to memory",
        suggested_fixture_candidate="add redacted fixture candidate" if classification.should_add_fixture else "",
        suggested_negative_control_candidate="add negative-control candidate" if classification.should_add_negative_control else "",
        suggested_claim_boundary_update="review claim boundary wording" if classification.should_update_claim_boundary else "",
        status="pending_review" if accepted else "rejected",
        must_not_claim=[
            "security_certification",
            "code_correctness_proof",
            "legal_privacy_license_eval_proof",
            "product_readiness",
            "quality_guarantee",
            "external_action_authorization",
        ],
    )


def memory_candidate_to_jsonable(candidate: FeedbackReplyMemoryCandidate) -> dict[str, Any]:
    return candidate.model_dump(mode="json", by_alias=True)
