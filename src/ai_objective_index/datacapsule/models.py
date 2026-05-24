from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


UseClass = Literal["train", "retrieve", "evaluate", "summarize", "share", "act"]
UseDecision = Literal[
    "ALLOW_USE",
    "HOLD_SOURCE_RIGHTS_REVIEW",
    "HOLD_PRIVACY_REVIEW",
    "HOLD_EVAL_LEAK_REVIEW",
    "HOLD_PROMPT_INJECTION_REVIEW",
    "HOLD_STALENESS_REVIEW",
    "BLOCK_ACTION_USE",
    "BLOCK_LICENSE_RESTRICTED",
    "BLOCK_PRIVACY_RISK",
    "BLOCK_UNSUPPORTED_CLAIM",
]
CapsuleDecision = Literal[
    "PASS_DATACAPSULE1_LOCAL_CAPSULE",
    "HOLD_DATACAPSULE1_REVIEW_REQUIRED",
    "BLOCK_DATACAPSULE1_USE_RISK",
    "PASS_DATACAPSULE2_LOCAL_CORPUS_MANIFEST",
    "HOLD_DATACAPSULE2_REVIEW_REQUIRED",
    "BLOCK_DATACAPSULE2_USE_RISK",
]
NegativeControlResult = Literal["PASS_NEGATIVE_CONTROL", "FAIL_NEGATIVE_CONTROL"]
ManifestSourceFormat = Literal["csv", "jsonl", "json"]
ManifestIntakeDecision = Literal[
    "PASS_DATACAPSULE3_MANIFEST_INTAKE",
    "HOLD_DATACAPSULE3_REVIEW_REQUIRED",
    "BLOCK_DATACAPSULE3_USE_RISK",
]
EvalLeakDecision = Literal[
    "PASS_EVAL_SEPARATION_LOCAL_METADATA",
    "HOLD_EVAL_LEAK_REVIEW",
    "BLOCK_EVAL_LEAK_CONFLICT",
]


DEFAULT_MUST_NOT_CLAIM = [
    "do not claim legal sufficiency",
    "do not claim privacy compliance",
    "do not claim data quality guarantee",
    "do not claim license clearance",
    "do not claim evaluation cleanliness",
    "do not claim action authorization",
    "do not claim purchasing advice",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class RiskFlags(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    privacy: bool = False
    poison: bool = False
    prompt_injection: bool = False
    eval_leak: bool = False
    stale: bool = False
    contradiction: bool = False
    rights_unknown: bool = False
    source_unknown: bool = False
    raw_indicators: list[str] = Field(default_factory=list)


class DataUseBoundary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    use_class: UseClass
    decision: UseDecision
    allowed: bool = False
    reasons: list[str] = Field(default_factory=list)
    evidence_required: list[str] = Field(default_factory=list)
    claim_ceiling: str = "local data-use boundary only; not legal, privacy, quality, or action authorization"


class DataUsePermission(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    train: DataUseBoundary
    retrieve: DataUseBoundary
    evaluate: DataUseBoundary
    summarize: DataUseBoundary
    share: DataUseBoundary
    act: DataUseBoundary


class DataCapsule(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule/v0.1", alias="schema")
    capsule_id: str
    data_id: str
    name: str
    source: str = ""
    raw_hash: str
    transform_chain: list[str] = Field(default_factory=list)
    license: str = "unknown"
    privacy_level: str = "unknown"
    source_records: list[str] = Field(default_factory=list)
    use_permissions: DataUsePermission
    risk_flags: RiskFlags = Field(default_factory=RiskFlags)
    residual_notes: list[str] = Field(default_factory=list)
    claim_ceiling: str = "local DataCapsule metadata receipt; not legal sufficiency, privacy compliance, data quality guarantee, or action authorization"
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    local_only: bool = True
    network_used: bool = False
    external_service_used: bool = False
    token_printed: bool = False
    can_certify_rights: bool = False
    can_certify_privacy: bool = False
    can_certify_quality: bool = False
    can_authorize_action: bool = False
    generated_at: str = Field(default_factory=timestamp)


class DataCapsuleBuildResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule_BuildResult/v0.1", alias="schema")
    result_id: str
    decision: CapsuleDecision
    metadata_path: str
    capsule_path: str
    report_path: str
    allow_count: int
    hold_count: int
    block_count: int
    capsule: DataCapsule
    local_only: bool = True
    network_used: bool = False
    crawler_used: bool = False
    external_service_used: bool = False
    token_printed: bool = False
    can_certify_rights: bool = False
    can_certify_privacy: bool = False
    can_certify_quality: bool = False
    can_authorize_action: bool = False
    known_limits: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    generated_at: str = Field(default_factory=timestamp)


class CorpusManifestFile(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    path: str
    source: str = ""
    license: str = "unknown"
    purpose: list[str] = Field(default_factory=list)
    privacy_level: str = "unknown"
    risk_flags: RiskFlags = Field(default_factory=RiskFlags)


class CorpusManifestSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    corpus_id: str
    name: str
    root_path: str = ""
    file_count: int
    source_record_count: int
    license_values: list[str] = Field(default_factory=list)
    privacy_levels: list[str] = Field(default_factory=list)
    risk_flags: RiskFlags = Field(default_factory=RiskFlags)
    missing_fields: list[str] = Field(default_factory=list)
    local_only: bool = True
    network_used: bool = False
    crawler_used: bool = False
    external_service_used: bool = False


class DataCapsuleNegativeControl(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    control_id: str
    control_goal: str
    expected_decision: str
    actual_decision: str
    result: NegativeControlResult
    findings: list[str] = Field(default_factory=list)


class DataCapsuleCorpusBuildResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule_CorpusBuildResult/v0.1", alias="schema")
    result_id: str
    decision: CapsuleDecision
    manifest_path: str
    capsule_path: str
    report_path: str
    summary: CorpusManifestSummary
    capsule: DataCapsule
    negative_controls: list[DataCapsuleNegativeControl] = Field(default_factory=list)
    negative_control_false_pass_count: int = 0
    local_only: bool = True
    network_used: bool = False
    crawler_used: bool = False
    external_service_used: bool = False
    token_printed: bool = False
    can_certify_rights: bool = False
    can_certify_privacy: bool = False
    can_certify_quality: bool = False
    can_authorize_action: bool = False
    known_limits: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    generated_at: str = Field(default_factory=timestamp)


class EvalLeakSeparationReport(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule_EvalLeakSeparationReport/v0.1", alias="schema")
    decision: EvalLeakDecision
    train_count: int = 0
    eval_count: int = 0
    overlap_count: int = 0
    overlap_paths: list[str] = Field(default_factory=list)
    hold_reasons: list[str] = Field(default_factory=list)
    local_only: bool = True
    network_used: bool = False
    crawler_used: bool = False
    external_service_used: bool = False
    can_prove_eval_cleanliness: bool = False
    generated_at: str = Field(default_factory=timestamp)


class DataCapsuleManifestIntakeResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule_ManifestIntakeResult/v0.1", alias="schema")
    result_id: str
    decision: ManifestIntakeDecision
    source_format: ManifestSourceFormat
    source_path: str
    normalized_manifest_path: str
    corpus_result_path: str
    eval_leak_report_path: str
    corpus_result: DataCapsuleCorpusBuildResult
    eval_leak_report: EvalLeakSeparationReport
    local_only: bool = True
    network_used: bool = False
    crawler_used: bool = False
    external_service_used: bool = False
    token_printed: bool = False
    can_certify_rights: bool = False
    can_certify_privacy: bool = False
    can_certify_quality: bool = False
    can_prove_eval_cleanliness: bool = False
    can_authorize_action: bool = False
    known_limits: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=lambda: list(DEFAULT_MUST_NOT_CLAIM))
    generated_at: str = Field(default_factory=timestamp)
