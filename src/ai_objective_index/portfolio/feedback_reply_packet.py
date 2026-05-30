from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ReplySource = Literal["sample_fixture", "local_file", "pasted_text_file", "manual_note", "unknown"]
ReviewerType = Literal[
    "owner",
    "maintainer",
    "internal",
    "external",
    "data_steward",
    "security_reviewer",
    "developer",
    "founder_operator",
    "unknown",
]
ReplyVertical = Literal["agentsec", "qira", "datacapsule", "portfolio", "unknown"]
ConsentSignal = Literal["explicit_local_review_allowed", "feedback_only", "unclear", "insufficient", "sample_fixture"]
RequestedAction = Literal[
    "clarify",
    "fix_finding",
    "add_evidence",
    "change_route",
    "request_second_run",
    "request_external_action",
    "request_certification",
    "other",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def feedback_reply_claim_boundary() -> dict[str, bool]:
    return {
        "not_reply_sending": True,
        "not_github_issue_creation": True,
        "not_security_certification": True,
        "not_code_correctness_proof": True,
        "not_legal_opinion": True,
        "not_privacy_audit": True,
        "not_license_clearance": True,
        "not_eval_clean_proof": True,
        "not_quality_guarantee": True,
        "not_product_ready": True,
        "no_external_action_authorization": True,
    }


def feedback_reply_must_not_do() -> list[str]:
    return [
        "send_email",
        "send_dm",
        "post_to_community",
        "call_github_api",
        "create_github_issue",
        "comment_on_pr",
        "create_pr",
        "merge",
        "deploy",
        "publish_package",
        "fetch_url",
        "crawl_or_scrape",
        "upload_data",
        "train_model",
        "use_credentials",
    ]


class FeedbackReplyPacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackReplyPacket/v0.1", alias="schema")
    reply_id: str
    generated_at: str = Field(default_factory=timestamp)
    source: ReplySource = "unknown"
    source_ref: str = ""
    reviewer_type: ReviewerType = "unknown"
    related_vertical: ReplyVertical = "unknown"
    related_artifact_refs: list[str] = Field(default_factory=list)
    reply_text_redacted: str
    contains_private_data_declared: bool = False
    consent_signal: ConsentSignal = "unclear"
    requested_action: RequestedAction = "other"
    external_action_requested: bool = False
    certification_or_readiness_claim_requested: bool = False
    token_or_secret_detected: bool = False
    private_kernel_detected: bool = False
    claim_boundary: dict[str, bool] = Field(default_factory=feedback_reply_claim_boundary)
    must_not_do: list[str] = Field(default_factory=feedback_reply_must_not_do)


def packet_to_jsonable(packet: FeedbackReplyPacket) -> dict[str, Any]:
    return packet.model_dump(mode="json", by_alias=True)


def sample_reply_texts() -> dict[str, str]:
    return {
        "agentsec": (
            "I reviewed the AgentSec sample. The permission HOLD is useful, but the readout should "
            "explain which manifest field caused the concern. I consent to local/offline review of "
            "this redacted sample note and would like a second local pass."
        ),
        "qira": (
            "For the QIRA sample, the release-side-effect BLOCK is understandable. Please add a "
            "local CI evidence request before any finding change. This is feedback only and local "
            "offline review is allowed for the sample."
        ),
        "datacapsule": (
            "The DataCapsule demo should make the action-use boundary clearer. Add a fixture showing "
            "that action use remains blocked when a manifest lacks separate authorization. Local "
            "sample review is allowed."
        ),
        "portfolio": (
            "The portfolio dashboard is understandable, but the feedback flow could show the next "
            "manual step more clearly. Please route this as portfolio messaging feedback; no outreach "
            "automation is requested."
        ),
    }


def sample_reply_paths() -> dict[str, Path]:
    base = Path("feedback_replies")
    return {
        "agentsec": base / "FEEDBACK_REPLY_SAMPLE_AGENTSEC.md",
        "qira": base / "FEEDBACK_REPLY_SAMPLE_QIRA.md",
        "datacapsule": base / "FEEDBACK_REPLY_SAMPLE_DATACAPSULE.md",
        "portfolio": base / "FEEDBACK_REPLY_SAMPLE_PORTFOLIO.md",
    }


def sample_packet_paths() -> dict[str, Path]:
    base = Path("feedback_replies")
    return {
        "agentsec": base / "FEEDBACK_REPLY_PACKET_SAMPLE_AGENTSEC.json",
        "qira": base / "FEEDBACK_REPLY_PACKET_SAMPLE_QIRA.json",
        "datacapsule": base / "FEEDBACK_REPLY_PACKET_SAMPLE_DATACAPSULE.json",
        "portfolio": base / "FEEDBACK_REPLY_PACKET_SAMPLE_PORTFOLIO.json",
    }
