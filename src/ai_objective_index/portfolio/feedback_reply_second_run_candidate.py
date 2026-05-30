from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .feedback_reply_classifier import FeedbackReplyClassification
from .feedback_reply_packet import FeedbackReplyPacket
from .feedback_reply_router import FeedbackReplyRoute


Readiness = Literal[
    "READY_FOR_LOCAL_SECOND_RUN",
    "HOLD_NEEDS_ARTIFACT",
    "HOLD_CONSENT_UNCLEAR",
    "BLOCK_EXTERNAL_ACTION",
    "BLOCK_SECRET",
    "BLOCK_OVERCLAIM",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def allowed_operations() -> list[str]:
    return ["local_redacted_review", "local_receipt_regeneration", "local_feedback_memory_update"]


def forbidden_operations() -> list[str]:
    return [
        "github_api",
        "external_posting",
        "external_repo_mutation",
        "merge",
        "deploy",
        "publish",
        "live_mcp_call",
        "upload_data",
        "train_model",
    ]


class FeedbackReplySecondRunCandidate(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackReplySecondRunCandidate/v0.1", alias="schema")
    second_run_candidate_id: str
    reply_id: str
    generated_at: str = Field(default_factory=timestamp)
    vertical: str
    required_artifacts: list[str] = Field(default_factory=list)
    allowed_operations: list[str] = Field(default_factory=allowed_operations)
    forbidden_operations: list[str] = Field(default_factory=forbidden_operations)
    readiness: Readiness
    next_actions: list[str] = Field(default_factory=list)
    execute_now: bool = False
    external_action_authorized: bool = False


def build_second_run_candidate(
    packet: FeedbackReplyPacket,
    classification: FeedbackReplyClassification,
    route: FeedbackReplyRoute,
) -> FeedbackReplySecondRunCandidate:
    if classification.classification == "BLOCK_EXTERNAL_ACTION_REQUEST":
        readiness: Readiness = "BLOCK_EXTERNAL_ACTION"
    elif classification.classification in {"BLOCK_SECRET_OR_PRIVATE_DATA", "BLOCK_PRIVATE_KERNEL_DISCLOSURE"}:
        readiness = "BLOCK_SECRET"
    elif classification.classification == "BLOCK_CERTIFICATION_OR_READINESS_CLAIM":
        readiness = "BLOCK_OVERCLAIM"
    elif classification.classification == "HOLD_CONSENT_UNCLEAR":
        readiness = "HOLD_CONSENT_UNCLEAR"
    elif route.can_create_second_run_candidate:
        readiness = "READY_FOR_LOCAL_SECOND_RUN"
    else:
        readiness = "HOLD_NEEDS_ARTIFACT"
    return FeedbackReplySecondRunCandidate(
        second_run_candidate_id=f"second-run-candidate-{packet.reply_id}",
        reply_id=packet.reply_id,
        vertical=route.selected_vertical,
        required_artifacts=route.required_next_artifacts or ["redacted local feedback note"],
        readiness=readiness,
        next_actions=[
            "run only local redaction and receipt regeneration",
            "do not send replies, create issues, post comments, call APIs, merge, deploy, publish, upload, or train",
        ],
    )


def second_run_candidate_to_jsonable(candidate: FeedbackReplySecondRunCandidate) -> dict[str, Any]:
    return candidate.model_dump(mode="json", by_alias=True)
