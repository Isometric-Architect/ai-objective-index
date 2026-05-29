from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class AgentSecPilotFeedbackMemoryEntry(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_AgentSecPilotFeedbackMemory/v0.1", alias="schema")
    pilot_id: str
    feedback_status: Literal["pending", "received", "incorporated", "closed"] = "pending"
    reviewer_type: Literal["owner", "maintainer", "internal", "external", "unknown"] = "unknown"
    issue_categories: list[str] = Field(default_factory=list)
    follow_up_actions: list[str] = Field(default_factory=list)
    should_update_policy_profile: bool = False
    should_add_negative_control: bool = False
    should_add_fixture: bool = False
    should_change_claim_boundary: bool = False
    timestamp: str = Field(default_factory=timestamp)
    external_posting_performed: bool = False
    token_printed: bool = False
    can_certify_security: bool = False
    can_authorize_action: bool = False


def build_feedback_memory_entry(receipt: dict[str, Any]) -> AgentSecPilotFeedbackMemoryEntry:
    decision_summary = receipt.get("decision_summary", {}) if isinstance(receipt.get("decision_summary"), dict) else {}
    hold_count = int(decision_summary.get("hold_count") or 0)
    block_count = int(decision_summary.get("block_count") or 0)
    categories = []
    for finding in receipt.get("findings", []) if isinstance(receipt.get("findings"), list) else []:
        if isinstance(finding, dict) and finding.get("category"):
            categories.append(str(finding["category"]))
    return AgentSecPilotFeedbackMemoryEntry(
        pilot_id=str(receipt.get("pilot_id", "agentsec-pilot-sample")),
        issue_categories=sorted(set(categories)),
        follow_up_actions=[
            "review HOLD/BLOCK findings with repository owner",
            "add public-safe fixture only if the pattern is generic and non-secret",
            "keep private policy calibration outside the public repository",
        ],
        should_update_policy_profile=bool(hold_count or block_count),
        should_add_negative_control=bool(block_count),
        should_add_fixture=bool(hold_count or block_count),
        should_change_claim_boundary=False,
    )
