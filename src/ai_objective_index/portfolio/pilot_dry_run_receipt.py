from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Vertical = Literal["agentsec", "qira", "datacapsule"]
TraceDecision = Literal["ALLOW", "HOLD", "BLOCK", "PASS", "SKIP"]
DryRunMode = Literal["local_sample"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def dry_run_must_not_claim() -> list[str]:
    return [
        "external_pilot",
        "security_certification",
        "code_correctness_proof",
        "legal_opinion",
        "privacy_audit",
        "license_clearance",
        "evaluation_cleanliness_proof",
        "quality_guarantee",
        "product_readiness",
        "external_action_authorization",
    ]


class PilotDryRunTraceStep(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    step_id: str
    step_name: str
    input_ref: str
    output_ref: str
    decision: TraceDecision = "PASS"
    notes: list[str] = Field(default_factory=list)


class PilotDryRunTrace(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotDryRunTrace/v0.1", alias="schema")
    dry_run_id: str
    generated_at: str = Field(default_factory=timestamp)
    intake_ids: list[str] = Field(default_factory=list)
    vertical_routes: list[dict[str, Any]] = Field(default_factory=list)
    executed_verticals: list[str] = Field(default_factory=list)
    skipped_verticals: list[str] = Field(default_factory=list)
    local_only: bool = True
    external_network_used: bool = False
    github_api_used: bool = False
    live_mcp_call_used: bool = False
    external_repo_modified: bool = False
    posting_or_commenting_performed: bool = False
    merge_deploy_publish_performed: bool = False
    raw_private_data_inspected: bool = False
    steps: list[PilotDryRunTraceStep] = Field(default_factory=list)


class PilotDryRunResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotDryRunResult/v0.1", alias="schema")
    dry_run_id: str
    vertical: Vertical
    intake_id: str
    selected_packager: str
    receipt_path: str
    gate_result: str
    allow_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    primary_decision: str = "UNKNOWN"
    redaction_status: str = "UNKNOWN"
    feedback_memory_status: str = "pending"
    known_limits: list[str] = Field(default_factory=list)
    claim_boundary: dict[str, bool] = Field(default_factory=dict)
    external_action_used: bool = False
    token_printed: bool = False


class PilotDryRunFeedbackMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotDryRunFeedbackMemory/v0.1", alias="schema")
    dry_run_id: str
    generated_at: str = Field(default_factory=timestamp)
    feedback_status: str = "pending"
    vertical_entries: list[dict[str, Any]] = Field(default_factory=list)
    portfolio_next_actions: list[str] = Field(default_factory=list)


class PilotDryRunReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotDryRunReceipt/v0.1", alias="schema")
    dry_run_id: str
    generated_at: str = Field(default_factory=timestamp)
    mode: DryRunMode = "local_sample"
    results: list[PilotDryRunResult] = Field(default_factory=list)
    aggregate_summary: dict[str, Any] = Field(default_factory=dict)
    feedback_memory: PilotDryRunFeedbackMemory
    claim_boundary: dict[str, bool] = Field(
        default_factory=lambda: {
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
        }
    )
    must_not_claim: list[str] = Field(default_factory=dry_run_must_not_claim)


def to_jsonable(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", by_alias=True)
