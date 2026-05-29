from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .datacapsule_pilot_receipt import timestamp


FeedbackStatus = Literal["pending", "received", "incorporated", "closed"]
ReviewerType = Literal["owner", "maintainer", "data_steward", "internal", "external", "unknown"]


class DataCapsulePilotFeedbackMemoryEntry(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DataCapsuleFeedbackMemory/v0.1", alias="schema")
    pilot_id: str
    feedback_status: FeedbackStatus = "pending"
    reviewer_type: ReviewerType = "unknown"
    issue_categories: list[str] = Field(default_factory=list)
    follow_up_actions: list[str] = Field(default_factory=list)
    should_update_manifest_schema: bool = False
    should_add_negative_control: bool = False
    should_add_fixture: bool = False
    should_change_claim_boundary: bool = False
    should_request_license_evidence: bool = False
    should_request_privacy_evidence: bool = False
    should_request_eval_split_evidence: bool = False
    timestamp: str = Field(default_factory=timestamp)
    external_posting_performed: bool = False
    external_network_used: bool = False
    token_printed: bool = False
    can_authorize_training: bool = False
    can_authorize_action: bool = False


def build_feedback_memory_entry(receipt: dict[str, Any]) -> DataCapsulePilotFeedbackMemoryEntry:
    findings = receipt.get("findings") if isinstance(receipt.get("findings"), list) else []
    categories = sorted({str(item.get("category", "unknown")) for item in findings if isinstance(item, dict)})
    decisions = {str(item.get("decision", "")) for item in findings if isinstance(item, dict)}
    return DataCapsulePilotFeedbackMemoryEntry(
        pilot_id=str(receipt.get("pilot_id", "datacapsule-pilot-unknown")),
        issue_categories=categories,
        follow_up_actions=[
            "review HOLD/BLOCK findings with data owner or data steward",
            "request license, terms, privacy, consent, and split-policy evidence",
            "add public-safe fixture only if the pattern is generic and non-secret",
            "keep private calibration outside the public repository",
        ],
        should_update_manifest_schema="HOLD" in decisions or "BLOCK" in decisions,
        should_add_negative_control="BLOCK" in decisions,
        should_add_fixture=True,
        should_change_claim_boundary=False,
        should_request_license_evidence=True,
        should_request_privacy_evidence=True,
        should_request_eval_split_evidence=True,
    )
