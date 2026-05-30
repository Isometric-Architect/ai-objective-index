from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


SkippedReason = Literal[
    "HOLD_NEEDS_ARTIFACT",
    "HOLD_CONSENT_UNCLEAR",
    "HOLD_CONTEXT_REQUIRED",
    "BLOCK_EXTERNAL_ACTION",
    "BLOCK_SECRET",
    "BLOCK_OVERCLAIM",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class SkippedCandidateReport(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackSecondRunSkippedReport/v0.1", alias="schema")
    candidate_id: str
    reply_id: str
    vertical: str
    generated_at: str = Field(default_factory=timestamp)
    reason: SkippedReason
    required_artifacts: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    can_retry_after_artifact: bool = False
    external_action_authorized: bool = False


def _reason(readiness: str) -> SkippedReason:
    if readiness == "HOLD_CONSENT_UNCLEAR":
        return "HOLD_CONSENT_UNCLEAR"
    if readiness == "BLOCK_EXTERNAL_ACTION":
        return "BLOCK_EXTERNAL_ACTION"
    if readiness == "BLOCK_SECRET":
        return "BLOCK_SECRET"
    if readiness == "BLOCK_OVERCLAIM":
        return "BLOCK_OVERCLAIM"
    if readiness.startswith("HOLD_"):
        return "HOLD_NEEDS_ARTIFACT"
    return "HOLD_CONTEXT_REQUIRED"


def build_skipped_report(candidate: dict[str, Any]) -> SkippedCandidateReport:
    readiness = str(candidate.get("readiness", "HOLD_NEEDS_ARTIFACT"))
    reason = _reason(readiness)
    required_artifacts = [str(item) for item in candidate.get("required_artifacts", [])]
    return SkippedCandidateReport(
        candidate_id=str(candidate.get("second_run_candidate_id", "unknown-candidate")),
        reply_id=str(candidate.get("reply_id", "unknown-reply")),
        vertical=str(candidate.get("vertical", "unknown")),
        reason=reason,
        required_artifacts=required_artifacts,
        unresolved_questions=[
            "candidate is not marked READY_FOR_LOCAL_SECOND_RUN",
            "local redacted artifact or consent may be missing",
        ],
        next_actions=[
            "collect redacted local artifact summary",
            "rerun feedback reply intake after artifact or consent is available",
            "do not execute, post, merge, deploy, publish, upload, train, fetch, or call APIs",
        ],
        can_retry_after_artifact=reason in {"HOLD_NEEDS_ARTIFACT", "HOLD_CONSENT_UNCLEAR", "HOLD_CONTEXT_REQUIRED"},
    )


def skipped_report_to_jsonable(report: SkippedCandidateReport) -> dict[str, Any]:
    return report.model_dump(mode="json", by_alias=True)
