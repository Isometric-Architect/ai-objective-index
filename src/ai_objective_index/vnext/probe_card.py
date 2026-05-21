from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


ProbeType = Literal[
    "source_trace_integrity",
    "missing_field_check",
    "policy_clarity_check",
    "docs_presence_check",
    "repository_presence_check",
    "license_presence_check",
    "unsupported_claim_check",
    "forbidden_action_check",
    "negative_control",
    "local_fixture",
]
ProbePlanScope = Literal["local_metadata_only", "local_fixture_only", "negative_control_only"]
ProbeResultToken = Literal[
    "PASS_LOCAL",
    "HOLD_INSUFFICIENT_EVIDENCE",
    "HOLD_POLICY_CLARITY",
    "HOLD_MISSING_FIELDS",
    "FAIL_EXPECTED_NEGATIVE_CONTROL",
    "FAIL_UNEXPECTED",
    "BLOCK_FORBIDDEN_ACTION",
    "BLOCK_UNSUPPORTED_CLAIM",
    "BLOCK_NETWORK_REQUIRED",
    "INVALID_PROBE",
]
ProbeRouteEffect = Literal[
    "NO_CHANGE",
    "ADD_WARNING",
    "DOWNGRADE_TO_HOLD",
    "DOWNGRADE_TO_BLOCK",
    "DO_NOT_UPGRADE",
]
ProbeMemoryStatus = Literal["NO_PROBES", "LOCAL_PROBES_AVAILABLE", "HOLD_SIGNALS", "BLOCK_SIGNALS", "MIXED_SIGNALS"]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def default_probe_must_not_claim() -> list[str]:
    return [
        "verified",
        "safe",
        "security certified",
        "quality guaranteed",
        "production ready",
        "external validation",
        "action authorization",
        "purchasing advice",
    ]


class ProbeSandboxPolicy(BaseModel):
    model_config = ConfigDict(extra="allow")

    no_network: bool = True
    no_external_tool_execution: bool = True
    no_subprocess: bool = True
    local_data_only: bool = True


class ProbeCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ProbeCard/v0.1", alias="schema")
    probe_id: str | None = None
    probe_type: ProbeType = "local_fixture"
    objective_id: str | None = None
    capability_id: str
    object_id: str | None = None
    name: str | None = None
    data_scope: str = "sample"
    probe_goal: str = "Run a deterministic local metadata probe before use."
    canary_input: dict[str, Any] | None = None
    expected_behavior: str | None = None
    negative_control_expected: str | None = None
    required_fields: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(
        default_factory=lambda: [
            "verified",
            "safe",
            "security certified",
            "quality guaranteed",
            "production ready",
            "official best",
            "purchasing advice",
        ]
    )
    forbidden_actions: list[str] = Field(
        default_factory=lambda: [
            "payment",
            "booking",
            "login",
            "email",
            "purchase",
            "contract",
            "supplier verification",
            "account connection",
        ]
    )
    sandbox_policy: ProbeSandboxPolicy = Field(default_factory=ProbeSandboxPolicy)
    claim_ceiling: str = "local metadata probe only; not verification, security certification, quality guarantee, or action authorization"
    generated_at: str = Field(default_factory=utc_now)

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        if "capability_id" not in payload and "target_capability" in payload:
            payload["capability_id"] = payload["target_capability"]
        if "objective_id" not in payload and "objective_scope" in payload:
            payload["objective_id"] = payload["objective_scope"]
        if "expected_behavior" not in payload and "pass_fail" in payload:
            payload["expected_behavior"] = f"Legacy pass_fail starts as {payload['pass_fail']}"
        if isinstance(payload.get("sandbox_policy"), str):
            payload["sandbox_policy"] = ProbeSandboxPolicy().model_dump()
        return payload

    @model_validator(mode="after")
    def ensure_probe_id(self) -> "ProbeCard":
        if not self.probe_id:
            self.probe_id = f"probe-{uuid4().hex[:12]}"
        return self


class ProbePlan(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ProbePlan/v0.1", alias="schema")
    plan_id: str | None = None
    objective_id: str | None = None
    route_request: dict[str, Any] | None = None
    capability_ids: list[str] = Field(default_factory=list)
    probe_cards: list[ProbeCard] = Field(default_factory=list)
    plan_scope: ProbePlanScope = "local_metadata_only"
    allowed_execution: list[str] = Field(default_factory=lambda: ["deterministic_local_only"])
    forbidden_execution: list[str] = Field(
        default_factory=lambda: [
            "network",
            "live_mcp_call",
            "external_tool",
            "shell_subprocess",
            "payment",
            "booking",
            "login",
            "email",
            "purchase",
            "contract",
        ]
    )
    expected_outputs: list[str] = Field(default_factory=lambda: ["ProbeReceipt", "ProbeRouteOverlay"])
    claim_ceiling: str = "local probe plan only; not verification, certification, quality guarantee, or action authorization"
    must_not_claim: list[str] = Field(default_factory=default_probe_must_not_claim)
    generated_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def ensure_plan_id(self) -> "ProbePlan":
        if not self.plan_id:
            self.plan_id = f"probe-plan-{uuid4().hex[:12]}"
        if not self.capability_ids:
            self.capability_ids = sorted({card.capability_id for card in self.probe_cards})
        return self


class ProbeResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ProbeResult/v0.1", alias="schema")
    probe_id: str
    capability_id: str
    result: ProbeResultToken
    checked_fields: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    can_influence_route: bool = True
    can_upgrade_to_verified: bool = False
    can_certify_security: bool = False
    can_certify_quality: bool = False
    can_authorize_action: bool = False


class ProbeReceiptAggregate(BaseModel):
    model_config = ConfigDict(extra="allow")

    pass_local_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    fail_unexpected_count: int = 0
    negative_control_pass_count: int = 0
    negative_control_fail_count: int = 0


class ProbeReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ProbeReceipt/v0.1", alias="schema")
    receipt_id: str | None = None
    plan_id: str
    probe_results: list[ProbeResult] = Field(default_factory=list)
    aggregate: ProbeReceiptAggregate = Field(default_factory=ProbeReceiptAggregate)
    route_effect: ProbeRouteEffect = "NO_CHANGE"
    claim_ceiling: str = "local probe receipt only; not verification, security certification, quality guarantee, or action authorization"
    generated_at: str = Field(default_factory=utc_now)
    token_printed: bool = False

    @model_validator(mode="after")
    def ensure_receipt_id(self) -> "ProbeReceipt":
        if not self.receipt_id:
            self.receipt_id = f"probe-receipt-{uuid4().hex[:12]}"
        return self


class CapabilityProbeMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_CapabilityProbeMemory/v0.1", alias="schema")
    capability_id: str
    probe_count: int = 0
    latest_probe_result: str | None = None
    hold_reasons: list[str] = Field(default_factory=list)
    block_reasons: list[str] = Field(default_factory=list)
    recurring_findings: list[str] = Field(default_factory=list)
    negative_control_status: str = "not_checked"
    can_influence_route: bool = False
    can_verify: bool = False
    can_certify_security: bool = False
    memory_status: ProbeMemoryStatus = "NO_PROBES"
    generated_at: str = Field(default_factory=utc_now)


class ProbeCapabilityOverlay(BaseModel):
    model_config = ConfigDict(extra="allow")

    capability_id: str
    probe_results: list[str] = Field(default_factory=list)
    overlay_notes: list[str] = Field(default_factory=list)
    decision_effect: ProbeRouteEffect = "NO_CHANGE"


class ProbeRouteOverlay(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_ProbeRouteOverlay/v0.1", alias="schema")
    route_request: dict[str, Any]
    original_route_summary: dict[str, Any]
    probe_plan_id: str | None = None
    probe_receipt_id: str | None = None
    probe_memory_applied: bool = False
    per_capability_probe_overlay: list[ProbeCapabilityOverlay] = Field(default_factory=list)
    final_claim_ceiling: str = "route with local probe overlay; not verified, not security certified, not a quality guarantee"
    must_not_claim: list[str] = Field(default_factory=default_probe_must_not_claim)
    generated_at: str = Field(default_factory=utc_now)
    external_execution: bool = False
    network_used: bool = False
    gateway_execution: bool = False
