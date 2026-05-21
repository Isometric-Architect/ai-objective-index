from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

ReceiptSubmittedBy = Literal["user", "agent", "local_test", "unknown"]
ReceiptOrigin = Literal["self_reported", "local_fixture", "public_issue", "manual_review", "benchmark", "unknown"]
ReceiptOutcome = Literal["success", "partial", "fail", "hold", "blocked"]
ReceiptEnvironment = Literal["local", "cloud", "browser", "api", "mcp_client", "unknown"]
ReceiptErrorType = Literal[
    "install_failure",
    "docs_missing",
    "policy_unclear",
    "source_trace_missing",
    "wrong_ranking",
    "stale_metadata",
    "api_failure",
    "security_concern",
    "unsupported_claim",
    "unknown",
]
ReceiptValidationDecision = Literal[
    "RECEIPT_ACCEPTED",
    "HOLD_MISSING_REQUIRED_FIELDS",
    "HOLD_LOW_EVIDENCE_ORIGIN",
    "HOLD_CONFLICTING_OUTCOME",
    "BLOCK_FORBIDDEN_ACTION",
    "BLOCK_UNSUPPORTED_CLAIM",
    "BLOCK_ACTION_AUTHORIZATION",
    "INVALID_RECEIPT",
]
ReceiptMemoryStatus = Literal[
    "NO_RECEIPTS",
    "RECEIPTS_AVAILABLE",
    "FAILURE_SIGNALS",
    "MIXED_SIGNALS",
    "HOLD_INSUFFICIENT_RECEIPTS",
]
ReceiptDecisionEffect = Literal[
    "NO_CHANGE",
    "ADD_WARNING",
    "DOWNGRADE_TO_HOLD",
    "DOWNGRADE_TO_BLOCK",
    "DO_NOT_UPGRADE",
]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def default_must_not_claim() -> list[str]:
    return [
        "verified",
        "safe",
        "security certified",
        "quality guaranteed",
        "production ready",
        "legal/financial/medical advice",
        "purchasing advice",
        "action authorization",
    ]


class ExecutionReceiptSubmission(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ExecutionReceiptSubmission/v0.1", alias="schema")
    receipt_id: str | None = None
    objective_id: str | None = None
    route_request_id: str | None = None
    capability_id: str
    object_id: str | None = None
    capability_name: str | None = None
    data_scope: str | None = None
    submitted_by: ReceiptSubmittedBy = "unknown"
    receipt_origin: ReceiptOrigin = "unknown"
    outcome: ReceiptOutcome
    outcome_summary: str = ""
    task_context: str = ""
    environment_class: ReceiptEnvironment = "unknown"
    constraints_checked: list[str] = Field(default_factory=list)
    observed_outputs: list[str] = Field(default_factory=list)
    error_type: ReceiptErrorType | None = None
    residual_found: bool = False
    residual_notes: list[str] = Field(default_factory=list)
    missing_fields_found: list[str] = Field(default_factory=list)
    source_trace_ids: list[str] = Field(default_factory=list)
    route_decision_before: str | None = None
    route_decision_after: str | None = None
    claim_ceiling: str = "receipt memory only; not verification, security certification, quality guarantee, or action authorization"
    must_not_claim: list[str] = Field(default_factory=default_must_not_claim)
    timestamp: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def ensure_receipt_id(self) -> "ExecutionReceiptSubmission":
        if not self.receipt_id:
            self.receipt_id = f"exec-receipt-{uuid4().hex[:12]}"
        return self


class ExecutionReceiptValidationResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ExecutionReceiptValidationResult/v0.1", alias="schema")
    receipt_id: str
    valid: bool
    decision: ReceiptValidationDecision
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    claim_ceiling: str = "receipt memory only; cannot certify safety, security, quality, legal compliance, product readiness, or action authorization"
    can_influence_route: bool = False
    can_upgrade_to_verified: bool = False
    can_certify_security: bool = False
    can_certify_quality: bool = False
    next_actions: list[str] = Field(default_factory=list)
    token_printed: bool = False


class StoredExecutionReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_StoredExecutionReceipt/v0.1", alias="schema")
    receipt: ExecutionReceiptSubmission
    validation: ExecutionReceiptValidationResult
    stored_at: str = Field(default_factory=utc_now)
    token_redacted: bool = False
    read_only_external: bool = True
    external_execution: bool = False


class CapabilityReceiptMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_CapabilityReceiptMemory/v0.1", alias="schema")
    capability_id: str
    receipt_count: int = 0
    outcome_counts: dict[str, int] = Field(default_factory=dict)
    last_outcome: str | None = None
    known_failures: list[str] = Field(default_factory=list)
    recurring_error_types: list[str] = Field(default_factory=list)
    residual_notes: list[str] = Field(default_factory=list)
    evidence_origins: list[str] = Field(default_factory=list)
    can_influence_route: bool = False
    must_not_claim: list[str] = Field(default_factory=default_must_not_claim)
    memory_status: ReceiptMemoryStatus = "NO_RECEIPTS"
    generated_at: str = Field(default_factory=utc_now)


class ObjectiveReceiptSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ObjectiveReceiptSummary/v0.1", alias="schema")
    objective_id: str
    receipt_count: int = 0
    capabilities_seen: list[str] = Field(default_factory=list)
    outcome_counts: dict[str, int] = Field(default_factory=dict)
    top_failure_modes: list[str] = Field(default_factory=list)
    route_adjustment_notes: list[str] = Field(default_factory=list)
    known_limits: list[str] = Field(
        default_factory=lambda: [
            "Receipt summaries are local memory, not independent verification.",
            "Success receipts cannot certify safety, security, quality, or product readiness.",
        ]
    )
    generated_at: str = Field(default_factory=utc_now)


class ReceiptCapabilityOverlay(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    capability_id: str
    receipt_count: int = 0
    outcome_signal: str = "none"
    failure_signal: str = "none"
    overlay_notes: list[str] = Field(default_factory=list)
    decision_effect: ReceiptDecisionEffect = "NO_CHANGE"


class ReceiptRouteOverlay(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ReceiptRouteOverlay/v0.1", alias="schema")
    route_request: dict[str, Any]
    original_route_summary: dict[str, Any]
    receipt_memory_applied: bool = False
    per_capability_overlay: list[ReceiptCapabilityOverlay] = Field(default_factory=list)
    final_claim_ceiling: str = "route decision with local receipt memory; not verified, not security certified, not a quality guarantee"
    generated_at: str = Field(default_factory=utc_now)
    must_not_claim: list[str] = Field(default_factory=default_must_not_claim)
    external_execution: bool = False
    probe_execution: bool = False
    gateway_execution: bool = False


def model_to_jsonable(model: BaseModel | dict[str, Any]) -> dict[str, Any]:
    if isinstance(model, BaseModel):
        return model.model_dump(mode="json", by_alias=True)
    return model
