from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .pilot_feedback_classifier import PilotFeedbackClassification
from .pilot_feedback_packet import PilotFeedbackPacket
from .pilot_second_run_plan import PilotSecondRunPlan


SecondRunGateDecision = Literal[
    "READY_FOR_LOCAL_SECOND_RUN",
    "HOLD_SECOND_RUN_CONTEXT",
    "HOLD_REDACTION_REVIEW",
    "BLOCK_EXTERNAL_ACTION",
    "BLOCK_SECRET_FINDING",
    "BLOCK_OVERCLAIM",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PilotSecondRunGate(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotSecondRunGate/v0.1", alias="schema")
    gate_id: str
    generated_at: str = Field(default_factory=timestamp)
    feedback_id: str
    dry_run_id: str
    decision: SecondRunGateDecision
    plan_status: str
    classification: str
    execute_now: bool = False
    external_action_authorized: bool = False
    reasons: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


def evaluate_second_run_gate(
    packet: PilotFeedbackPacket,
    classification: PilotFeedbackClassification,
    plan: PilotSecondRunPlan,
) -> PilotSecondRunGate:
    reasons: list[str] = []
    if classification.classification == "BLOCK_EXTERNAL_ACTION_REQUEST" or plan.run_status == "BLOCK_EXTERNAL_ACTION":
        decision: SecondRunGateDecision = "BLOCK_EXTERNAL_ACTION"
        reasons.append("feedback or plan requests forbidden external action")
    elif classification.classification == "BLOCK_SECRET_OR_PRIVATE_DATA" or plan.run_status == "BLOCK_SECRET_FINDING":
        decision = "BLOCK_SECRET_FINDING"
        reasons.append("feedback or plan contains secret/private-data risk")
    elif classification.classification == "BLOCK_CERTIFICATION_CLAIM" or plan.run_status == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
        reasons.append("feedback asks for certification/proof/readiness claim")
    elif plan.run_status == "HOLD_REDACTION":
        decision = "HOLD_REDACTION_REVIEW"
        reasons.append("feedback requires redaction review before a second pass")
    elif plan.run_status == "READY_FOR_LOCAL_SECOND_RUN":
        decision = "READY_FOR_LOCAL_SECOND_RUN"
        reasons.append("local redacted consent-bounded second-run plan is ready, but not executed by default")
    else:
        decision = "HOLD_SECOND_RUN_CONTEXT"
        reasons.append("more context, consent, or local artifacts are needed before second-run planning can proceed")
    return PilotSecondRunGate(
        gate_id=f"second-run-gate-{packet.feedback_id}",
        feedback_id=packet.feedback_id,
        dry_run_id=packet.dry_run_id,
        decision=decision,
        plan_status=plan.run_status,
        classification=classification.classification,
        reasons=reasons,
        next_actions=plan.next_actions,
    )


def second_run_gate_to_jsonable(gate: PilotSecondRunGate) -> dict[str, Any]:
    return gate.model_dump(mode="json", by_alias=True)
