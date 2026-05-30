from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .feedback_reply_packet import FeedbackReplyPacket


Classification = Literal[
    "ACCEPT_FEEDBACK_MEMORY_CANDIDATE",
    "ACCEPT_SECOND_RUN_CANDIDATE",
    "HOLD_NEEDS_MORE_CONTEXT",
    "HOLD_CONSENT_UNCLEAR",
    "HOLD_REDACTION_REVIEW",
    "HOLD_MANUAL_TRIAGE",
    "BLOCK_SECRET_OR_PRIVATE_DATA",
    "BLOCK_EXTERNAL_ACTION_REQUEST",
    "BLOCK_CERTIFICATION_OR_READINESS_CLAIM",
    "BLOCK_PRIVATE_KERNEL_DISCLOSURE",
]
Severity = Literal["info", "low", "medium", "high", "critical", "unknown"]

EXTERNAL_ACTION_PATTERNS = [
    re.compile(r"\b(create|open)\s+(?:a\s+)?(?:github\s+)?issue\b", re.I),
    re.compile(r"\b(comment|post|send|dm)\b", re.I),
    re.compile(r"\bmerge\b|\bdeploy\b|\bpublish\b", re.I),
    re.compile(r"\bfetch\s+url\b|\bclone\s+(?:the\s+)?repo\b|\bcall\s+(?:the\s+)?api\b", re.I),
]
CERTIFICATION_PATTERNS = [
    re.compile(r"\bcertif(?:y|ied|ication)\b", re.I),
    re.compile(r"\bprove(?:n)?\s+(?:correct|safe|compliant)\b", re.I),
    re.compile(r"\bproduct[-\s]+ready\b|\bproduction[-\s]+ready\b", re.I),
    re.compile(r"\blegal\s+clearance\b|\bprivacy\s+clearance\b|\blicense\s+clearance\b", re.I),
    re.compile(r"\bquality\s+guarantee\b|\beval[-\s]+clean\s+proof\b", re.I),
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class FeedbackReplyClassification(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackReplyClassification/v0.1", alias="schema")
    classification_id: str
    reply_id: str
    generated_at: str = Field(default_factory=timestamp)
    classification: Classification
    severity: Severity = "info"
    issue_categories: list[str] = Field(default_factory=list)
    affected_verticals: list[str] = Field(default_factory=list)
    affected_artifacts: list[str] = Field(default_factory=list)
    should_update_finding: bool = False
    should_update_claim_boundary: bool = False
    should_add_negative_control: bool = False
    should_add_fixture: bool = False
    should_request_evidence: bool = False
    should_run_second_pass: bool = False
    reason: str = ""
    next_actions: list[str] = Field(default_factory=list)
    external_action_authorized: bool = False
    certification_authorized: bool = False


def _has(patterns: list[re.Pattern[str]], text: str) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def classify_feedback_reply(packet: FeedbackReplyPacket) -> FeedbackReplyClassification:
    text = packet.reply_text_redacted
    next_actions = [
        "keep reply processing local/offline",
        "do not send, post, create GitHub issues, call APIs, fetch URLs, upload, train, merge, deploy, or publish",
        "preserve claim boundaries",
    ]
    categories: list[str] = [packet.requested_action]

    if packet.token_or_secret_detected or packet.contains_private_data_declared:
        return FeedbackReplyClassification(
            classification_id=f"classification-{packet.reply_id}",
            reply_id=packet.reply_id,
            classification="BLOCK_SECRET_OR_PRIVATE_DATA",
            severity="critical",
            issue_categories=categories + ["secret_or_private_data"],
            affected_verticals=[packet.related_vertical],
            affected_artifacts=packet.related_artifact_refs,
            reason="reply declares or contains secret/private-data risk",
            next_actions=next_actions + ["ask for a redacted local summary instead"],
        )
    if packet.private_kernel_detected:
        return FeedbackReplyClassification(
            classification_id=f"classification-{packet.reply_id}",
            reply_id=packet.reply_id,
            classification="BLOCK_PRIVATE_KERNEL_DISCLOSURE",
            severity="critical",
            issue_categories=categories + ["private_kernel"],
            affected_verticals=[packet.related_vertical],
            affected_artifacts=packet.related_artifact_refs,
            reason="reply appears to disclose private-kernel details",
            next_actions=next_actions + ["remove private kernel details before intake"],
        )
    if packet.external_action_requested or packet.requested_action == "request_external_action" or _has(EXTERNAL_ACTION_PATTERNS, text):
        return FeedbackReplyClassification(
            classification_id=f"classification-{packet.reply_id}",
            reply_id=packet.reply_id,
            classification="BLOCK_EXTERNAL_ACTION_REQUEST",
            severity="high",
            issue_categories=categories + ["external_action_request"],
            affected_verticals=[packet.related_vertical],
            affected_artifacts=packet.related_artifact_refs,
            reason="reply requests an external action that feedback intake cannot authorize",
            next_actions=next_actions + ["convert the request into a local artifact note if review is still useful"],
        )
    if (
        packet.certification_or_readiness_claim_requested
        or packet.requested_action == "request_certification"
        or _has(CERTIFICATION_PATTERNS, text)
    ):
        return FeedbackReplyClassification(
            classification_id=f"classification-{packet.reply_id}",
            reply_id=packet.reply_id,
            classification="BLOCK_CERTIFICATION_OR_READINESS_CLAIM",
            severity="high",
            issue_categories=categories + ["certification_or_readiness_request"],
            affected_verticals=[packet.related_vertical],
            affected_artifacts=packet.related_artifact_refs,
            should_update_claim_boundary=True,
            reason="reply asks for certification, proof, clearance, readiness, or guarantee language",
            next_actions=next_actions + ["rewrite the request as local/offline receipt wording"],
        )
    if len(text.strip()) < 24:
        return FeedbackReplyClassification(
            classification_id=f"classification-{packet.reply_id}",
            reply_id=packet.reply_id,
            classification="HOLD_NEEDS_MORE_CONTEXT",
            severity="low",
            issue_categories=categories + ["unclear_feedback"],
            affected_verticals=[packet.related_vertical],
            affected_artifacts=packet.related_artifact_refs,
            reason="reply is too short to classify confidently",
            next_actions=next_actions + ["request a clearer local feedback note"],
        )
    if packet.consent_signal in {"unclear", "insufficient"} and packet.requested_action == "request_second_run":
        return FeedbackReplyClassification(
            classification_id=f"classification-{packet.reply_id}",
            reply_id=packet.reply_id,
            classification="HOLD_CONSENT_UNCLEAR",
            severity="medium",
            issue_categories=categories + ["consent_gap"],
            affected_verticals=[packet.related_vertical],
            affected_artifacts=packet.related_artifact_refs,
            should_request_evidence=True,
            reason="reply asks for a second pass but consent is not clear enough",
            next_actions=next_actions + ["request explicit local/offline review consent"],
        )
    should_second = packet.requested_action == "request_second_run" and packet.consent_signal in {
        "explicit_local_review_allowed",
        "sample_fixture",
    }
    return FeedbackReplyClassification(
        classification_id=f"classification-{packet.reply_id}",
        reply_id=packet.reply_id,
        classification="ACCEPT_SECOND_RUN_CANDIDATE" if should_second else "ACCEPT_FEEDBACK_MEMORY_CANDIDATE",
        severity="low",
        issue_categories=categories,
        affected_verticals=[packet.related_vertical],
        affected_artifacts=packet.related_artifact_refs,
        should_update_finding=packet.requested_action in {"clarify", "fix_finding", "add_evidence"},
        should_add_fixture=packet.requested_action in {"add_evidence", "request_second_run"},
        should_request_evidence=packet.requested_action in {"add_evidence", "request_second_run"},
        should_run_second_pass=should_second,
        reason="reply is local/offline, claim-bounded, and usable as a memory or second-run candidate",
        next_actions=next_actions + ["create local triage and feedback memory candidate"],
    )


def classification_to_jsonable(classification: FeedbackReplyClassification) -> dict[str, Any]:
    return classification.model_dump(mode="json", by_alias=True)
