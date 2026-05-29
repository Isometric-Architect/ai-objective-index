from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .pilot_feedback_classifier import PilotFeedbackClassification
from .pilot_feedback_packet import PilotFeedbackPacket, feedback_must_not_claim


RunStatus = Literal[
    "NOT_RUN",
    "READY_FOR_LOCAL_SECOND_RUN",
    "HOLD_MISSING_ARTIFACTS",
    "HOLD_REDACTION",
    "BLOCK_EXTERNAL_ACTION",
    "BLOCK_SECRET_FINDING",
    "BLOCK_OVERCLAIM",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def default_allowed_operations() -> list[str]:
    return [
        "local_receipt_regeneration",
        "local_redaction_check",
        "local_claim_boundary_check",
        "local_feedback_memory_update",
    ]


def default_forbidden_operations() -> list[str]:
    return [
        "github_api",
        "clone_repo",
        "fetch_url",
        "create_issue",
        "comment_on_pr",
        "merge",
        "deploy",
        "publish_package",
        "live_mcp_call",
        "external_tool_execution",
        "upload_data",
        "train_model",
    ]


class PilotSecondRunPlan(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotSecondRunPlan/v0.1", alias="schema")
    plan_id: str
    feedback_id: str
    dry_run_id: str
    generated_at: str = Field(default_factory=timestamp)
    verticals_to_rerun: list[str] = Field(default_factory=list)
    artifacts_to_reuse: list[str] = Field(default_factory=list)
    artifacts_needed: list[str] = Field(default_factory=list)
    allowed_operations: list[str] = Field(default_factory=default_allowed_operations)
    forbidden_operations: list[str] = Field(default_factory=default_forbidden_operations)
    expected_outputs: list[str] = Field(
        default_factory=lambda: [
            "updated_receipt",
            "second_run_readout",
            "feedback_memory_update",
            "unresolved_questions",
        ]
    )
    run_status: RunStatus = "NOT_RUN"
    claim_ceiling: str = "local/offline second-run planning artifact only"
    next_actions: list[str] = Field(default_factory=list)
    execute_now: bool = False
    external_action_authorized: bool = False
    must_not_claim: list[str] = Field(default_factory=feedback_must_not_claim)


def build_second_run_plan(packet: PilotFeedbackPacket, classification: PilotFeedbackClassification) -> PilotSecondRunPlan:
    classification_id = classification.classification
    artifacts_needed: list[str] = []
    if classification.should_request_evidence:
        artifacts_needed.append("redacted local evidence summary")
    if classification.should_add_fixture:
        artifacts_needed.append("redacted fixture candidate")
    if classification.should_add_negative_control:
        artifacts_needed.append("redacted negative-control candidate")
    if not artifacts_needed:
        artifacts_needed.append("clarified local feedback note")

    if classification_id == "BLOCK_EXTERNAL_ACTION_REQUEST":
        status: RunStatus = "BLOCK_EXTERNAL_ACTION"
    elif classification_id == "BLOCK_SECRET_OR_PRIVATE_DATA":
        status = "BLOCK_SECRET_FINDING"
    elif classification_id == "BLOCK_CERTIFICATION_CLAIM":
        status = "BLOCK_OVERCLAIM"
    elif classification_id == "HOLD_REDACTION_REVIEW":
        status = "HOLD_REDACTION"
    elif classification_id in {"HOLD_NEEDS_MORE_CONTEXT", "HOLD_OWNER_CONFIRMATION", "HOLD_MANUAL_TRIAGE"}:
        status = "HOLD_MISSING_ARTIFACTS"
    elif classification.should_run_second_pass and packet.consent_status in {"self_owned", "owner_provided", "sample_fixture"}:
        status = "READY_FOR_LOCAL_SECOND_RUN"
    else:
        status = "NOT_RUN"

    return PilotSecondRunPlan(
        plan_id=f"second-run-plan-{packet.feedback_id}",
        feedback_id=packet.feedback_id,
        dry_run_id=packet.dry_run_id,
        verticals_to_rerun=[packet.vertical] if packet.vertical in {"agentsec", "qira", "datacapsule"} else [],
        artifacts_to_reuse=packet.affected_artifact_refs,
        artifacts_needed=artifacts_needed,
        run_status=status,
        next_actions=[
            "keep the second-run plan local/offline",
            "run redaction before any receipt regeneration",
            "reuse only local receipt/readout artifacts",
            "do not execute the second run by default",
            "do not post, merge, deploy, publish, fetch, clone, upload, train, or call external APIs",
        ],
    )


def second_run_plan_to_jsonable(plan: PilotSecondRunPlan) -> dict[str, Any]:
    return plan.model_dump(mode="json", by_alias=True)
