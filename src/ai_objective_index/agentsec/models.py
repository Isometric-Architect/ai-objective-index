from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


IntegrationType = Literal["mcp_server", "tool_manifest", "api", "agent_tool", "unknown"]
RiskDecision = Literal[
    "ALLOW_METADATA_ONLY",
    "HOLD_REVIEW_REQUIRED",
    "BLOCK_FORBIDDEN_ACTION",
    "BLOCK_UNSUPPORTED_CLAIM",
]
ScanDecision = Literal[
    "PASS_AGENTSEC1_LOCAL_SCAN",
    "HOLD_AGENTSEC1_REVIEW_REQUIRED",
    "BLOCK_AGENTSEC1_MANIFEST_RISK",
]


DEFAULT_MUST_NOT_CLAIM = [
    "do not claim verified tool status",
    "do not claim safety",
    "do not claim security certification",
    "do not claim quality guarantee",
    "do not claim production readiness",
    "do not claim external action authorization",
    "do not claim legal compliance",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PermissionScope(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    network_access: bool = False
    file_access: bool = False
    write_access: bool = False
    secret_access: bool = False
    browser_access: bool = False
    code_execution: bool = False
    raw_indicators: list[str] = Field(default_factory=list)


class ToolRiskPacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AgentSec_ToolRiskPacket/v0.1", alias="schema")
    packet_id: str
    tool_id: str
    name: str
    provider: str = "unknown"
    manifest_path: str = "<memory>"
    metadata_hash: str
    integration_type: IntegrationType = "unknown"
    permission_scope: PermissionScope = Field(default_factory=PermissionScope)
    hidden_instruction_findings: list[str] = Field(default_factory=list)
    prompt_injection_findings: list[str] = Field(default_factory=list)
    namespace_findings: list[str] = Field(default_factory=list)
    forbidden_action_findings: list[str] = Field(default_factory=list)
    unsupported_claim_findings: list[str] = Field(default_factory=list)
    risk_decision: RiskDecision = "HOLD_REVIEW_REQUIRED"
    allowed_use: list[str] = Field(default_factory=lambda: ["local metadata review"])
    hold_use: list[str] = Field(default_factory=list)
    blocked_use: list[str] = Field(default_factory=list)
    residual_notes: list[str] = Field(default_factory=list)
    claim_ceiling: str = "local metadata risk packet only; not verification or security certification"
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    generated_at: str = Field(default_factory=timestamp)


class AgentSecActionBoundaryReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AgentSec_ActionBoundaryReceipt/v0.1", alias="schema")
    receipt_id: str
    packet_id: str
    decision: RiskDecision
    allowed_actions: list[str] = Field(default_factory=lambda: ["local metadata review"])
    hold_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    no_network: bool = True
    no_live_mcp_call: bool = True
    no_external_tool_execution: bool = True
    can_certify_security: bool = False
    can_certify_quality: bool = False
    can_authorize_action: bool = False
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    generated_at: str = Field(default_factory=timestamp)


class AgentSecScanResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AgentSec_ScanResult/v0.1", alias="schema")
    scan_id: str
    decision: ScanDecision
    manifest_path: str
    packet_count: int
    allow_count: int
    hold_count: int
    block_count: int
    packets: list[ToolRiskPacket]
    receipts: list[AgentSecActionBoundaryReceipt] = Field(default_factory=list)
    local_only: bool = True
    network_used: bool = False
    live_mcp_called: bool = False
    external_tool_executed: bool = False
    token_printed: bool = False
    known_limits: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    generated_at: str = Field(default_factory=timestamp)
