from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Decision = Literal["ALLOW", "HOLD", "BLOCK"]
Severity = Literal["info", "low", "medium", "high", "critical", "unknown"]
Category = Literal[
    "permission_scope",
    "hidden_instruction",
    "namespace_lookalike",
    "unsupported_claim",
    "forbidden_action",
    "missing_source",
    "docs_gap",
    "schema_gap",
    "unknown",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class OwnerConsent(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    status: Literal["owner_provided", "self_owned", "sample_fixture", "unknown"] = "sample_fixture"
    evidence_note: str = "sample fixture only; no external owner consent record is stored"


class InputManifest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    source_type: Literal["local_file", "fixture", "pasted_manifest", "generated_sample"] = "fixture"
    path_or_id: str
    hash: str = ""


class ReviewScope(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    manifest_only: bool = True
    live_tool_execution: bool = False
    live_mcp_call: bool = False
    github_api_call: bool = False
    external_network: bool = False


class PacketSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    manifest_count: int = 0
    tool_count: int = 0
    permission_count: int = 0
    hidden_instruction_findings: int = 0
    namespace_findings: int = 0
    unsupported_claim_findings: int = 0
    forbidden_action_findings: int = 0


class DecisionSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    top_hold_reasons: list[str] = Field(default_factory=list)
    top_block_reasons: list[str] = Field(default_factory=list)


class FindingCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    finding_id: str
    severity: Severity = "unknown"
    decision: Decision = "HOLD"
    category: Category = "unknown"
    evidence_ref: str
    explanation: str
    next_action: str
    must_not_claim: list[str] = Field(default_factory=list)


class ClaimBoundary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    not_security_certification: bool = True
    not_quality_guarantee: bool = True
    not_compliance_audit: bool = True
    no_live_execution: bool = True
    no_external_action_authorization: bool = True


class ReceiptFeedbackMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    entry_id: str
    suggested_next_review: str
    unresolved_questions: list[str] = Field(default_factory=list)
    known_limits: list[str] = Field(default_factory=list)


class AgentSecPilotReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_AgentSecPilotReceipt/v0.1", alias="schema")
    pilot_id: str
    generated_at: str = Field(default_factory=timestamp)
    project_label: str
    repo_url: str = ""
    owner_consent: OwnerConsent
    input_manifest: InputManifest
    review_scope: ReviewScope = Field(default_factory=ReviewScope)
    packet_summary: PacketSummary = Field(default_factory=PacketSummary)
    decision_summary: DecisionSummary = Field(default_factory=DecisionSummary)
    findings: list[FindingCard] = Field(default_factory=list)
    claim_boundary: ClaimBoundary = Field(default_factory=ClaimBoundary)
    feedback_memory: ReceiptFeedbackMemory
    external_actions_performed: bool = False
    workflow_enabled: bool = False
    github_api_used: bool = False
    live_mcp_called: bool = False
    external_tool_executed: bool = False
    token_printed: bool = False
    private_kernel_exposed: bool = False


def must_not_claim() -> list[str]:
    return [
        "verification status",
        "tool safety guarantee",
        "security certification",
        "quality guarantee",
        "production readiness",
        "compliance audit",
        "live security scan",
        "external action authorization",
    ]


def receipt_to_jsonable(receipt: AgentSecPilotReceipt) -> dict[str, Any]:
    return receipt.model_dump(mode="json", by_alias=True)
