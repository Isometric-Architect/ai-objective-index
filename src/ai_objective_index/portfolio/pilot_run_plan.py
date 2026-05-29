from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .pilot_intake_packet import default_forbidden_actions
from .pilot_vertical_router import PilotVerticalRoute


ReceiptTarget = Literal[
    "agentsec_pilot_receipt",
    "qira_pilot_receipt",
    "datacapsule_pilot_receipt",
    "hold_manual_triage",
]
RunStatus = Literal[
    "NOT_RUN",
    "READY_FOR_LOCAL_SAMPLE",
    "READY_FOR_OWNER_CONSENTED_LOCAL_REVIEW",
    "HOLD_CONSENT",
    "HOLD_REDACTION",
    "BLOCK_FORBIDDEN_ACTION",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PilotRunPlan(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotRunPlan/v0.1", alias="schema")
    plan_id: str
    intake_id: str
    generated_at: str = Field(default_factory=timestamp)
    selected_vertical: str
    allowed_operations: list[str] = Field(default_factory=lambda: ["local_static_review", "redaction_preflight", "vertical_route_check", "receipt_packaging"])
    forbidden_operations: list[str] = Field(default_factory=default_forbidden_actions)
    expected_outputs: list[str] = Field(default_factory=list)
    receipt_target: ReceiptTarget = "hold_manual_triage"
    preflight_checks: list[str] = Field(default_factory=lambda: ["consent_check", "redaction_check", "vertical_route_check", "claim_boundary_check"])
    run_status: RunStatus = "NOT_RUN"
    next_actions: list[str] = Field(default_factory=list)
    external_action_used: bool = False
    live_execution_used: bool = False


def build_run_plan(route: PilotVerticalRoute, consent_status: str, redaction_decision: str = "PASS_REDACTED") -> PilotRunPlan:
    if route.selected_vertical == "agentsec":
        target: ReceiptTarget = "agentsec_pilot_receipt"
        outputs = ["AgentSec pilot receipt", "reviewer readout", "feedback memory entry"]
    elif route.selected_vertical == "qira":
        target = "qira_pilot_receipt"
        outputs = ["QIRA pilot receipt", "reviewer readout", "feedback memory entry"]
    elif route.selected_vertical == "datacapsule":
        target = "datacapsule_pilot_receipt"
        outputs = ["DataCapsule pilot receipt", "reviewer readout", "feedback memory entry"]
    else:
        target = "hold_manual_triage"
        outputs = ["manual triage note", "redaction request", "consent clarification"]

    if route.selected_vertical == "block_forbidden_artifact":
        status: RunStatus = "BLOCK_FORBIDDEN_ACTION"
    elif consent_status in {"unknown", "insufficient"} or route.selected_vertical == "block_insufficient_consent":
        status = "HOLD_CONSENT"
    elif redaction_decision != "PASS_REDACTED":
        status = "HOLD_REDACTION"
    elif route.can_generate_pilot_receipt:
        status = "READY_FOR_OWNER_CONSENTED_LOCAL_REVIEW" if consent_status == "owner_provided" else "READY_FOR_LOCAL_SAMPLE"
    else:
        status = "NOT_RUN"

    return PilotRunPlan(
        plan_id=f"run-plan-{route.intake_id}",
        intake_id=route.intake_id,
        selected_vertical=route.selected_vertical,
        expected_outputs=outputs,
        receipt_target=target,
        run_status=status,
        next_actions=[
            "confirm consent scope",
            "keep artifact local",
            "run redaction before pilot packaging",
            "package a local/offline receipt only",
            "do not post, merge, deploy, upload, train, fetch, clone, or call external APIs",
        ],
    )


def run_plan_to_jsonable(plan: PilotRunPlan) -> dict[str, Any]:
    return plan.model_dump(mode="json", by_alias=True)
