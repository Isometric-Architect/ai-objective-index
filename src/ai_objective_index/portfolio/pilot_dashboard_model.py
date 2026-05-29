from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


DashboardMode = Literal["static_local_artifact"]
DashboardPhase = Literal["pilot_receipt", "portfolio", "intake", "dry_run", "feedback", "second_run"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def dashboard_claim_boundary() -> dict[str, bool]:
    return {
        "not_external_pilot": True,
        "not_security_certification": True,
        "not_code_correctness_proof": True,
        "not_legal_opinion": True,
        "not_privacy_audit": True,
        "not_license_clearance": True,
        "not_eval_clean_proof": True,
        "not_quality_guarantee": True,
        "not_product_ready": True,
        "no_external_action_authorization": True,
        "static_local_only": True,
    }


class PilotStatusCard(BaseModel):
    model_config = ConfigDict(extra="allow")

    vertical: str
    display_name: str
    reviewed_object: str
    current_phase: DashboardPhase = "second_run"
    primary_decision: str
    allow_count: int
    hold_count: int
    block_count: int
    redaction_status: str
    feedback_status: str
    second_run_status: str
    latest_gate_status: str
    top_hold_reason: str
    top_block_reason: str
    next_action: str
    must_not_claim: list[str] = Field(default_factory=list)


class PilotDashboard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotDashboard/v0.1", alias="schema")
    dashboard_id: str
    generated_at: str = Field(default_factory=timestamp)
    mode: DashboardMode = "static_local_artifact"
    lifecycle_summary: dict[str, bool] = Field(default_factory=dict)
    verticals: list[str] = Field(default_factory=lambda: ["agentsec", "qira", "datacapsule"])
    aggregate_counts: dict[str, int] = Field(default_factory=dict)
    vertical_status_cards: list[dict[str, Any]] = Field(default_factory=list)
    gate_status: dict[str, str] = Field(default_factory=dict)
    feedback_memory_summary: dict[str, Any] = Field(default_factory=dict)
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    claim_boundary: dict[str, bool] = Field(default_factory=dashboard_claim_boundary)
    known_limits: list[str] = Field(default_factory=list)
    recommended_next_package: str = "ROE-17 External-Safe Demo/Share Pack"
    external_action_count: int = 0
    token_printed: bool = False
    private_kernel_exposed: bool = False


def status_card_to_jsonable(card: PilotStatusCard) -> dict[str, Any]:
    return card.model_dump(mode="json")


def dashboard_to_jsonable(dashboard: PilotDashboard) -> dict[str, Any]:
    return dashboard.model_dump(mode="json", by_alias=True)
