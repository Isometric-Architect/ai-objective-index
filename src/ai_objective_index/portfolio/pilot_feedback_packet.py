from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


FeedbackVertical = Literal["agentsec", "qira", "datacapsule", "portfolio", "unknown"]
ReviewerType = Literal["owner", "maintainer", "internal", "external", "data_steward", "unknown"]
FeedbackSource = Literal["local_form", "sample_fixture", "pasted_text", "manual_review", "unknown"]
ConsentStatus = Literal["self_owned", "owner_provided", "sample_fixture", "insufficient", "unknown"]
FeedbackCategory = Literal[
    "wrong_finding",
    "missing_evidence",
    "unclear_explanation",
    "wrong_vertical_route",
    "wrong_allow_hold_block",
    "missing_claim_boundary",
    "overclaim_concern",
    "redaction_concern",
    "add_negative_control",
    "add_fixture",
    "request_second_run",
    "other",
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def feedback_claim_boundary() -> dict[str, bool]:
    return {
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


def feedback_must_not_do() -> list[str]:
    return [
        "call_github_api",
        "create_issue",
        "comment_on_pr",
        "create_pr",
        "merge",
        "deploy",
        "publish_package",
        "clone_repo",
        "fetch_url",
        "crawl_or_scrape",
        "live_mcp_call",
        "external_tool_execution",
        "upload_data",
        "train_model",
        "use_credentials",
    ]


def feedback_must_not_claim() -> list[str]:
    return [
        "security_certification",
        "code_correctness_proof",
        "legal_clearance",
        "privacy_clearance",
        "license_clearance",
        "eval_clean_proof",
        "quality_guarantee",
        "product_readiness",
        "external_action_authorization",
    ]


class PilotFeedbackPacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotFeedbackPacket/v0.1", alias="schema")
    feedback_id: str
    generated_at: str = Field(default_factory=timestamp)
    dry_run_id: str
    vertical: FeedbackVertical
    reviewer_type: ReviewerType = "unknown"
    feedback_source: FeedbackSource = "unknown"
    consent_status: ConsentStatus = "unknown"
    feedback_category: FeedbackCategory
    feedback_text: str
    affected_artifact_refs: list[str] = Field(default_factory=list)
    requested_change: str = ""
    proposed_evidence_refs: list[str] = Field(default_factory=list)
    contains_private_data_declared: bool = False
    external_action_requested: bool = False
    claim_boundary: dict[str, bool] = Field(default_factory=feedback_claim_boundary)
    must_not_do: list[str] = Field(default_factory=feedback_must_not_do)
    must_not_claim: list[str] = Field(default_factory=feedback_must_not_claim)


def sample_feedback_packets(dry_run_id: str = "roe13-local-sample-dry-run-v0-1") -> list[PilotFeedbackPacket]:
    return [
        PilotFeedbackPacket(
            feedback_id="pilot-feedback-sample-agentsec-v0-1",
            dry_run_id=dry_run_id,
            vertical="agentsec",
            reviewer_type="maintainer",
            feedback_source="sample_fixture",
            consent_status="sample_fixture",
            feedback_category="request_second_run",
            feedback_text="Please run a second local pass after adding a clearer permission-scope explanation for the manifest-only finding.",
            affected_artifact_refs=["pilot_dry_runs/ROE13_PILOT_DRY_RUN_RESULT_AGENTSEC.json"],
            requested_change="clarify permission-scope explanation and regenerate the local receipt readout",
            proposed_evidence_refs=["pilot_receipts/agentsec/AGENTSEC_PILOT_RECEIPT_SAMPLE.json"],
        ),
        PilotFeedbackPacket(
            feedback_id="pilot-feedback-sample-qira-v0-1",
            dry_run_id=dry_run_id,
            vertical="qira",
            reviewer_type="internal",
            feedback_source="sample_fixture",
            consent_status="sample_fixture",
            feedback_category="missing_evidence",
            feedback_text="The release-side-effect BLOCK is useful, but the next pass should ask for a redacted local CI summary before changing the finding.",
            affected_artifact_refs=["pilot_dry_runs/ROE13_PILOT_DRY_RUN_RESULT_QIRA.json"],
            requested_change="request local CI evidence before a second receipt pass",
            proposed_evidence_refs=["pilot_receipts/qira/QIRA_CI_EVIDENCE_SUMMARY_SAMPLE.json"],
        ),
        PilotFeedbackPacket(
            feedback_id="pilot-feedback-sample-datacapsule-v0-1",
            dry_run_id=dry_run_id,
            vertical="datacapsule",
            reviewer_type="data_steward",
            feedback_source="sample_fixture",
            consent_status="sample_fixture",
            feedback_category="add_fixture",
            feedback_text="Add a sample fixture for an explicit action-use denial and keep the second run local and manifest-only.",
            affected_artifact_refs=["pilot_dry_runs/ROE13_PILOT_DRY_RUN_RESULT_DATACAPSULE.json"],
            requested_change="add fixture candidate and schedule a local second-pass plan",
            proposed_evidence_refs=["pilot_receipts/datacapsule/DATACAPSULE_USE_BOUNDARY_SAMPLE.json"],
        ),
    ]


def feedback_packet_to_jsonable(packet: PilotFeedbackPacket) -> dict[str, Any]:
    return packet.model_dump(mode="json", by_alias=True)
