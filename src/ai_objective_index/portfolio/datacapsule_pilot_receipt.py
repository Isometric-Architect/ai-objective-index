from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


OwnerConsentStatus = Literal["self_owned", "owner_provided", "public_sample", "sample_fixture", "unknown"]
ManifestSourceType = Literal["local_manifest", "sample_fixture", "public_dataset_card", "repository_metadata", "pasted_manifest", "unknown"]
DataCategory = Literal["text", "code", "images", "audio", "video", "tabular", "logs", "metadata", "mixed", "unknown"]
DeclaredStatus = Literal["none", "possible", "present", "unknown"]
DeclaredTriState = Literal["yes", "no", "partial", "unknown"]
UseDecision = Literal["ALLOW", "HOLD", "BLOCK"]
FindingSeverity = Literal["info", "low", "medium", "high", "critical", "unknown"]
FindingDecision = Literal["ALLOW", "HOLD", "BLOCK"]
FindingCategory = Literal[
    "source_rights",
    "license_gap",
    "privacy_risk",
    "consent_gap",
    "eval_leakage",
    "stale_data",
    "share_boundary",
    "train_boundary",
    "retrieve_boundary",
    "act_boundary",
    "commercial_boundary",
    "unknown",
]
RightsStatus = Literal[
    "SOURCE_RIGHTS_DECLARED",
    "HOLD_RIGHTS_UNCLEAR",
    "HOLD_LICENSE_MISSING",
    "BLOCK_DISALLOWED_USE_DECLARED",
    "UNKNOWN",
]
PrivacyStatus = Literal[
    "LOW_MANIFEST_RISK",
    "HOLD_PII_UNKNOWN",
    "HOLD_CONSENT_UNKNOWN",
    "HOLD_DEIDENTIFICATION_UNKNOWN",
    "BLOCK_DECLARED_SENSITIVE_DATA",
    "UNKNOWN",
]
LeakageStatus = Literal[
    "LOW_MANIFEST_RISK",
    "HOLD_EVAL_OVERLAP_UNKNOWN",
    "HOLD_SPLIT_POLICY_MISSING",
    "BLOCK_DECLARED_EVAL_CONTAMINATION",
    "UNKNOWN",
]
CapsuleDecision = Literal[
    "ALLOW_MANIFEST_REVIEW_ARTIFACT",
    "HOLD_RIGHTS_REVIEW",
    "HOLD_PRIVACY_REVIEW",
    "HOLD_EVAL_LEAKAGE_REVIEW",
    "HOLD_STALENESS_REVIEW",
    "BLOCK_DECLARED_DISALLOWED_USE",
    "BLOCK_SENSITIVE_DATA",
    "BLOCK_ACTION_USE",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def datacapsule_must_not_claim() -> list[str]:
    return [
        "legal_clearance",
        "privacy_compliance",
        "license_clearance",
        "evaluation_cleanliness_proof",
        "data_quality_guarantee",
        "training_authorization",
        "action_authorization",
    ]


class OwnerConsent(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    status: OwnerConsentStatus = "sample_fixture"
    evidence_note: str = "sample/local owner consent metadata only"


class DataCapsuleCorpusManifest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DataCapsuleCorpusManifest/v0.1", alias="schema")
    manifest_id: str
    generated_at: str = Field(default_factory=timestamp)
    corpus_label: str
    owner_consent: OwnerConsent = Field(default_factory=OwnerConsent)
    source_type: ManifestSourceType = "sample_fixture"
    data_categories: list[DataCategory] = Field(default_factory=lambda: ["text", "metadata"])
    declared_sources: list[str] = Field(default_factory=list)
    declared_license: str = "unknown"
    declared_terms: str = "unknown"
    declared_collection_method: str = "unknown"
    declared_update_date: str = "unknown"
    declared_pii_status: DeclaredStatus = "unknown"
    declared_eval_overlap_status: DeclaredStatus = "unknown"
    declared_allowed_uses: list[str] = Field(default_factory=list)
    declared_disallowed_uses: list[str] = Field(default_factory=list)
    declared_retention_policy: str = "unknown"
    declared_share_policy: str = "unknown"
    local_manifest_only: bool = True
    raw_content_inspected: bool = False
    external_network_used: bool = False
    claim_ceiling: str = "local/offline corpus manifest review artifact only"


class DataCapsuleSourceRightsSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DataCapsuleSourceRightsSummary/v0.1", alias="schema")
    summary_id: str
    manifest_id: str
    license_found: bool = False
    terms_found: bool = False
    source_attribution_found: bool = False
    collection_method_found: bool = False
    redistribution_allowed_declared: bool | None = None
    training_allowed_declared: bool | None = None
    retrieval_allowed_declared: bool | None = None
    evaluation_allowed_declared: bool | None = None
    commercial_use_declared: bool | None = None
    rights_status: RightsStatus = "UNKNOWN"
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=datacapsule_must_not_claim)


class DataCapsulePrivacyRiskSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DataCapsulePrivacyRiskSummary/v0.1", alias="schema")
    summary_id: str
    manifest_id: str
    pii_declared: DeclaredStatus = "unknown"
    sensitive_data_declared: DeclaredStatus = "unknown"
    deidentification_declared: DeclaredTriState = "unknown"
    consent_declared: DeclaredTriState = "unknown"
    privacy_status: PrivacyStatus = "UNKNOWN"
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=datacapsule_must_not_claim)


class DataCapsuleEvalLeakageSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DataCapsuleEvalLeakageSummary/v0.1", alias="schema")
    summary_id: str
    manifest_id: str
    eval_overlap_declared: DeclaredStatus = "unknown"
    benchmark_contamination_declared: DeclaredStatus = "unknown"
    split_policy_declared: DeclaredTriState = "unknown"
    leakage_status: LeakageStatus = "UNKNOWN"
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=datacapsule_must_not_claim)


class DataCapsuleUseBoundary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DataCapsuleUseBoundary/v0.1", alias="schema")
    boundary_id: str
    manifest_id: str
    train_use: UseDecision = "HOLD"
    retrieve_use: UseDecision = "HOLD"
    evaluate_use: UseDecision = "HOLD"
    share_use: UseDecision = "HOLD"
    act_use: UseDecision = "BLOCK"
    commercial_use: UseDecision = "HOLD"
    reasons: list[str] = Field(default_factory=list)
    blocked_uses: list[str] = Field(default_factory=list)
    hold_uses: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    claim_ceiling: str = "manifest-only use boundary; not legal/privacy/license/evaluation proof"
    must_not_claim: list[str] = Field(default_factory=datacapsule_must_not_claim)


class DecisionSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    top_hold_reasons: list[str] = Field(default_factory=list)
    top_block_reasons: list[str] = Field(default_factory=list)


class DataCapsuleFindingCard(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    finding_id: str
    severity: FindingSeverity = "unknown"
    decision: FindingDecision
    category: FindingCategory = "unknown"
    evidence_ref: str
    explanation: str
    next_action: str
    must_not_claim: list[str] = Field(default_factory=datacapsule_must_not_claim)


class DataCapsuleClaimBoundary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    not_legal_opinion: bool = True
    not_privacy_audit: bool = True
    not_license_clearance: bool = True
    not_eval_clean_proof: bool = True
    not_data_quality_guarantee: bool = True
    no_training_authorization: bool = True
    no_action_authorization: bool = True
    raw_content_not_inspected: bool = True


class DataCapsuleReceiptFeedbackMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    entry_id: str
    suggested_next_review: str
    unresolved_questions: list[str] = Field(default_factory=list)
    known_limits: list[str] = Field(default_factory=list)


class DataCapsulePilotReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DataCapsulePilotReceipt/v0.1", alias="schema")
    pilot_id: str
    generated_at: str = Field(default_factory=timestamp)
    corpus_manifest: DataCapsuleCorpusManifest
    source_rights_summary: DataCapsuleSourceRightsSummary
    privacy_risk_summary: DataCapsulePrivacyRiskSummary
    eval_leakage_summary: DataCapsuleEvalLeakageSummary
    use_boundary: DataCapsuleUseBoundary
    decision_summary: DecisionSummary
    findings: list[DataCapsuleFindingCard] = Field(default_factory=list)
    capsule_decision: CapsuleDecision = "HOLD_RIGHTS_REVIEW"
    claim_boundary: DataCapsuleClaimBoundary = Field(default_factory=DataCapsuleClaimBoundary)
    feedback_memory: DataCapsuleReceiptFeedbackMemory
    raw_content_inspected: bool = False
    external_network_used: bool = False
    crawler_used: bool = False
    data_uploaded: bool = False
    model_trained: bool = False
    external_api_used: bool = False
    github_api_used: bool = False
    token_printed: bool = False
    private_kernel_exposed: bool = False
    can_certify_rights: bool = False
    can_certify_privacy: bool = False
    can_certify_quality: bool = False
    can_prove_eval_cleanliness: bool = False
    can_authorize_training: bool = False
    can_authorize_action: bool = False


def to_jsonable(model: BaseModel) -> dict:
    return model.model_dump(mode="json", by_alias=True)
