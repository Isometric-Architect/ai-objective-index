from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


OwnerConsentStatus = Literal["self_owned", "owner_provided", "sample_fixture", "unknown"]
InputSource = Literal["local_patch", "local_diff_fixture", "sample_patch", "ci_artifact", "manual_review"]
ChangeType = Literal["bugfix", "refactor", "docs", "tests", "packaging", "security_sensitive", "release_config", "unknown"]
ClassificationDecision = Literal[
    "ALLOW_REVIEW",
    "HOLD_NEEDS_TEST_EVIDENCE",
    "HOLD_NEEDS_OWNER_REVIEW",
    "HOLD_SECURITY_REVIEW",
    "BLOCK_FORBIDDEN_ACTION",
    "BLOCK_SECRET_RISK",
]
EvidenceStatus = Literal["NO_CI_EVIDENCE", "PARTIAL_CI_EVIDENCE", "LOCAL_FIXTURE_EVIDENCE", "COPIED_CI_EVIDENCE"]
FindingSeverity = Literal["info", "low", "medium", "high", "critical", "unknown"]
FindingDecision = Literal["ALLOW", "HOLD", "BLOCK"]
FindingCategory = Literal[
    "patch_scope",
    "missing_test_evidence",
    "behavior_contract_gap",
    "ci_evidence_gap",
    "secret_risk",
    "external_action_risk",
    "release_side_effect",
    "dependency_risk",
    "reviewer_required",
    "unknown",
]
ReleaseGateDecision = Literal[
    "ALLOW_REVIEW_ARTIFACT",
    "HOLD_TEST_EVIDENCE",
    "HOLD_OWNER_REVIEW",
    "HOLD_SECURITY_REVIEW",
    "BLOCK_SECRET_RISK",
    "BLOCK_EXTERNAL_ACTION",
    "BLOCK_RELEASE_SIDE_EFFECT",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def qira_must_not_claim() -> list[str]:
    return [
        "correctness_proven",
        "security_certified",
        "quality_guaranteed",
        "production_ready",
        "merge_authorized",
        "deploy_authorized",
        "external_repo_mutation_allowed",
    ]


class OwnerConsent(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    status: OwnerConsentStatus = "sample_fixture"
    evidence_note: str = "sample/local owner consent metadata only"


class AllowedReviewScope(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    local_static_review: bool = True
    local_test_summary_intake: bool = True
    github_api_call: bool = False
    external_repo_modification: bool = False
    merge_or_deploy: bool = False


class QIRATaskPacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_QIRA_TaskPacket/v0.1", alias="schema")
    task_id: str
    generated_at: str = Field(default_factory=timestamp)
    task_title: str
    task_goal: str
    repo_label: str = ""
    owner_consent: OwnerConsent = Field(default_factory=OwnerConsent)
    input_source: InputSource = "sample_patch"
    intended_change_type: ChangeType = "tests"
    allowed_review_scope: AllowedReviewScope = Field(default_factory=AllowedReviewScope)
    forbidden_actions: list[str] = Field(
        default_factory=lambda: [
            "create_pr",
            "merge",
            "deploy",
            "publish_package",
            "comment_on_pr",
            "mutate_external_repo",
            "use_live_credentials",
        ]
    )
    claim_ceiling: str = "local/offline release-gate review artifact only"


class QIRAPatchClassification(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_QIRA_PatchClassification/v0.1", alias="schema")
    patch_id: str
    task_id: str
    files_changed_count: int
    file_categories: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    classification_decision: ClassificationDecision = "HOLD_NEEDS_TEST_EVIDENCE"
    evidence_refs: list[str] = Field(default_factory=list)
    explanation: str = ""
    next_actions: list[str] = Field(default_factory=list)


class QIRABehaviorContract(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_QIRA_BehaviorContract/v0.1", alias="schema")
    contract_id: str
    task_id: str
    expected_behavior: list[str] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)
    forbidden_behavior: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(
        default_factory=lambda: [
            "tests_pass",
            "docs_updated",
            "no_secret_diff",
            "no_unapproved_network",
            "no_release_side_effect",
            "reviewer_ack",
        ]
    )
    negative_controls: list[str] = Field(
        default_factory=lambda: [
            "secret_in_diff_must_block",
            "deploy_script_change_must_hold",
            "auth_scope_change_must_hold",
            "missing_test_evidence_must_hold",
        ]
    )
    claim_boundary: dict[str, bool] = Field(
        default_factory=lambda: {
            "not_correctness_proof": True,
            "not_security_certification": True,
            "not_production_readiness": True,
            "no_merge_authorization": True,
        }
    )


class QIRACIEvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_QIRA_CIEvidenceSummary/v0.1", alias="schema")
    ci_evidence_id: str
    task_id: str
    source_type: Literal["local_fixture", "copied_ci_summary", "generated_sample", "unknown"] = "generated_sample"
    tests_passed: bool | None = None
    tests_failed: int | None = None
    lint_passed: bool | None = None
    typecheck_passed: bool | None = None
    build_passed: bool | None = None
    coverage_reported: bool | None = None
    evidence_status: EvidenceStatus = "PARTIAL_CI_EVIDENCE"
    missing_evidence: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=qira_must_not_claim)


class DecisionSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    top_hold_reasons: list[str] = Field(default_factory=list)
    top_block_reasons: list[str] = Field(default_factory=list)


class QIRAFindingCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    finding_id: str
    severity: FindingSeverity = "unknown"
    decision: FindingDecision
    category: FindingCategory = "unknown"
    evidence_ref: str
    explanation: str
    next_action: str
    must_not_claim: list[str] = Field(default_factory=qira_must_not_claim)


class QIRAClaimBoundary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    not_code_correctness_proof: bool = True
    not_security_certification: bool = True
    not_quality_guarantee: bool = True
    no_merge_authorization: bool = True
    no_deploy_authorization: bool = True
    no_external_repo_mutation: bool = True


class QIRAReceiptFeedbackMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    entry_id: str
    suggested_next_review: str
    unresolved_questions: list[str] = Field(default_factory=list)
    known_limits: list[str] = Field(default_factory=list)


class QIRAPilotReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_QIRA_PilotReceipt/v0.1", alias="schema")
    pilot_id: str
    generated_at: str = Field(default_factory=timestamp)
    task_packet: QIRATaskPacket
    patch_classification: QIRAPatchClassification
    behavior_contract: QIRABehaviorContract
    ci_evidence_summary: QIRACIEvidenceSummary
    decision_summary: DecisionSummary
    findings: list[QIRAFindingCard] = Field(default_factory=list)
    release_gate_decision: ReleaseGateDecision = "HOLD_TEST_EVIDENCE"
    claim_boundary: QIRAClaimBoundary = Field(default_factory=QIRAClaimBoundary)
    feedback_memory: QIRAReceiptFeedbackMemory
    github_api_used: bool = False
    external_repo_modified: bool = False
    external_actions_performed: bool = False
    merge_performed: bool = False
    deploy_performed: bool = False
    publish_performed: bool = False
    token_printed: bool = False
    private_kernel_exposed: bool = False
    can_prove_correctness: bool = False
    can_certify_security: bool = False
    can_guarantee_quality: bool = False
    can_authorize_merge: bool = False
    can_authorize_deploy: bool = False


def to_jsonable(model: BaseModel) -> dict:
    return model.model_dump(mode="json", by_alias=True)
