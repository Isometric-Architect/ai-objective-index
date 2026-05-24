from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


PatchAction = Literal["patch_draft", "pr_open", "merge", "deploy", "public_claim"]
EvidenceOrigin = Literal["self_reported", "local_fixture", "ci_fixture", "manual_review", "unknown"]
DecisionToken = Literal[
    "PASS_CONTRACT_SCOPED",
    "HOLD_NEEDS_CONTRACT",
    "HOLD_TEST_HARNESS_ONLY_PASS",
    "HOLD_CI_PASS_CONTRACT_GAP",
    "HOLD_PROVENANCE_GAP",
    "HOLD_PATCH_APPLY_FAILURE",
    "BLOCK_FORBIDDEN_CHANGE",
    "BLOCK_ACTION_OVERCLAIM",
    "BLOCK_RAW_ECO_OVERCLAIM",
    "BLOCK_PATCH_PATH_ESCAPE",
]
ActionDecision = Literal["ALLOW", "ALLOW_SCOPED_INTERNAL", "HOLD", "BLOCK"]


DEFAULT_MUST_NOT_CLAIM = [
    "do not claim verified status",
    "do not claim safety",
    "do not claim security certification",
    "do not claim quality guarantee",
    "do not claim production readiness",
    "do not claim legal compliance",
    "do not claim deployment approval",
    "do not claim external action authorization",
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


class BehaviorContract(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_BehaviorContract/v0.1", alias="schema")
    contract_id: str
    task: str
    repo_scope: str = "local_or_fixture_repo"
    expected_behavior: list[str] = Field(default_factory=list)
    forbidden_changes: list[str] = Field(default_factory=lambda: [".env", ".pypirc", "credentials", "secrets"])
    required_evidence: list[str] = Field(default_factory=lambda: ["changed_files", "test_result", "patch_summary"])
    test_command_scope: dict[str, Any] = Field(
        default_factory=lambda: {
            "local_only": True,
            "no_network": True,
            "no_external_services": True,
            "no_secret_access": True,
            "no_deploy": True,
        }
    )
    claim_ceiling: str = "local release-gate receipt; not verification; not security certification; not deployment approval"
    created_at: str = Field(default_factory=_timestamp)


class PatchCandidate(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_PatchCandidate/v0.1", alias="schema")
    patch_id: str
    contract_id: str
    summary: str
    changed_files: list[str] = Field(default_factory=list)
    tests_passed: bool = False
    test_summary: str = ""
    evidence_origin: EvidenceOrigin = "unknown"
    requested_action: PatchAction = "patch_draft"
    declared_claims: list[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=_timestamp)


class ValidatorPacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_ValidatorPacket/v0.1", alias="schema")
    validator_id: str
    contract_id: str
    checks: list[str] = Field(default_factory=list)
    sandbox_policy: dict[str, Any] = Field(
        default_factory=lambda: {
            "local_data_only": True,
            "no_network": True,
            "no_external_tool_execution": True,
            "no_subprocess_for_arbitrary_tools": True,
            "no_deploy": True,
        }
    )
    generated_at: str = Field(default_factory=_timestamp)


class ResidualLedger(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_ResidualLedger/v0.1", alias="schema")
    ledger_id: str
    contract_id: str
    patch_id: str
    residuals: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    forbidden_change_findings: list[str] = Field(default_factory=list)
    unsupported_claim_findings: list[str] = Field(default_factory=list)
    decision_token: DecisionToken = "HOLD_NEEDS_CONTRACT"
    d_raw_status: str = "not_assessed_as_truth"
    d_eco_status: str = "not_assessed_as_ecosystem_readiness"
    generated_at: str = Field(default_factory=_timestamp)


class ActionLicense(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_ActionLicense/v0.1", alias="schema")
    license_id: str
    patch_id: str
    patch_draft: ActionDecision = "HOLD"
    pr_open: ActionDecision = "HOLD"
    merge: ActionDecision = "HOLD"
    deploy: ActionDecision = "BLOCK"
    public_claim: ActionDecision = "HOLD"
    decision_reason: str
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    generated_at: str = Field(default_factory=_timestamp)


class PatchReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_PatchReceipt/v0.1", alias="schema")
    receipt_id: str
    contract: BehaviorContract
    patch: PatchCandidate
    validator: ValidatorPacket
    residual_ledger: ResidualLedger
    action_license: ActionLicense
    claim_ceiling: str = "scoped local release-gate receipt only"
    can_verify_security: bool = False
    can_certify_quality: bool = False
    can_authorize_deploy: bool = False
    generated_at: str = Field(default_factory=_timestamp)


class QiraReleaseGateReport(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_ReleaseGateReport/v0.1", alias="schema")
    report_id: str
    decision_token: DecisionToken
    action_license: ActionLicense
    receipt: PatchReceipt
    summary: dict[str, Any]
    known_limits: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    external_actions_performed: bool = False
    pypi_upload_performed: bool = False
    mcp_registry_submission_performed: bool = False
    community_post_performed: bool = False
    token_printed: bool = False
    generated_at: str = Field(default_factory=_timestamp)
