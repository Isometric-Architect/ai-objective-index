from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RequestedVertical = Literal["agentsec", "qira", "datacapsule", "auto_route", "unknown"]
OwnerConsentStatus = Literal["self_owned", "owner_provided", "sample_fixture", "unknown"]
ArtifactType = Literal[
    "mcp_manifest",
    "tool_manifest",
    "pr_diff",
    "patch_text",
    "ci_summary",
    "dataset_manifest",
    "corpus_manifest",
    "dataset_card",
    "mixed",
    "unknown",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def pilot_must_not_claim() -> list[str]:
    return [
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


def default_forbidden_actions() -> list[str]:
    return [
        "clone_repo",
        "fetch_url",
        "call_github_api",
        "create_pr",
        "create_issue",
        "comment_on_pr",
        "merge",
        "deploy",
        "publish_package",
        "upload_data",
        "train_model",
        "live_mcp_call",
        "external_tool_execution",
        "use_credentials",
    ]


class IntakeOwnerConsent(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    status: OwnerConsentStatus = "sample_fixture"
    consent_text: str = "sample fixture for local/offline intake planning only"
    consent_scope: str = "local static review of explicitly provided sample metadata only"
    contact_redacted: bool = True


class ProvidedArtifact(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    artifact_type: ArtifactType = "unknown"
    local_path: str = ""
    pasted_text_id: str = ""
    hash: str = ""
    raw_content_included: bool = False
    contains_private_data_declared: bool | None = None


class AllowedReviewScope(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    local_static_review: bool = True
    manifest_only: bool = False
    diff_only: bool = False
    raw_data_inspection: bool = False
    external_network: bool = False
    github_api_call: bool = False
    live_tool_execution: bool = False
    external_repo_mutation: bool = False
    posting_or_commenting: bool = False


class IntakeClaimBoundary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    not_security_certification: bool = True
    not_code_correctness_proof: bool = True
    not_legal_opinion: bool = True
    not_privacy_audit: bool = True
    not_license_clearance: bool = True
    not_eval_clean_proof: bool = True
    not_quality_guarantee: bool = True
    not_product_ready: bool = True
    no_external_action_authorization: bool = True


class PilotIntakePacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotIntakePacket/v0.1", alias="schema")
    intake_id: str
    generated_at: str = Field(default_factory=timestamp)
    pilot_label: str
    requested_vertical: RequestedVertical = "auto_route"
    owner_consent: IntakeOwnerConsent = Field(default_factory=IntakeOwnerConsent)
    provided_artifact: ProvidedArtifact = Field(default_factory=ProvidedArtifact)
    allowed_review_scope: AllowedReviewScope = Field(default_factory=AllowedReviewScope)
    forbidden_actions: list[str] = Field(default_factory=default_forbidden_actions)
    claim_boundary: IntakeClaimBoundary = Field(default_factory=IntakeClaimBoundary)
    must_not_claim: list[str] = Field(default_factory=pilot_must_not_claim)
    external_action_requested: bool = False
    token_printed: bool = False
    private_kernel_exposed: bool = False


def intake_packet_to_jsonable(packet: PilotIntakePacket) -> dict[str, Any]:
    return packet.model_dump(mode="json", by_alias=True)
