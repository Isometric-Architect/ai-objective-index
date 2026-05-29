from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def default_safety_rules() -> dict[str, bool]:
    return {
        "no_block_to_allow_without_explicit_evidence": True,
        "no_hold_to_allow_without_evidence": True,
        "no_certification_upgrade": True,
        "no_external_action_authorization": True,
    }


class SecondRunDelta(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_SecondRunDelta/v0.1", alias="schema")
    delta_id: str
    generated_at: str = Field(default_factory=timestamp)
    vertical: str
    prior_receipt_ref: str
    new_receipt_ref: str
    feedback_ref: str
    changed_findings: list[dict[str, Any]] = Field(default_factory=list)
    unchanged_findings: list[str] = Field(default_factory=list)
    added_fixtures: list[dict[str, Any]] = Field(default_factory=list)
    added_negative_control_candidates: list[dict[str, Any]] = Field(default_factory=list)
    updated_explanations: list[str] = Field(default_factory=list)
    updated_next_actions: list[str] = Field(default_factory=list)
    claim_boundary_changes: list[str] = Field(default_factory=list)
    decision_changes: dict[str, int] = Field(
        default_factory=lambda: {
            "allow_to_hold_count": 0,
            "hold_to_allow_count": 0,
            "hold_to_block_count": 0,
            "block_to_hold_count": 0,
            "block_to_allow_count": 0,
        }
    )
    safety_rules: dict[str, bool] = Field(default_factory=default_safety_rules)
    unsafe_decision_upgrade_detected: bool = False
    certification_upgrade_detected: bool = False
    external_action_authorized: bool = False


def build_delta_from_result(result: dict[str, Any]) -> SecondRunDelta:
    prior_summary = result.get("prior_decision_summary", {})
    new_summary = result.get("new_decision_summary", {})
    decision_changes = {
        "allow_to_hold_count": max(0, int(prior_summary.get("allow_count", 0)) - int(new_summary.get("allow_count", 0))),
        "hold_to_allow_count": 0,
        "hold_to_block_count": max(0, int(new_summary.get("block_count", 0)) - int(prior_summary.get("block_count", 0))),
        "block_to_hold_count": 0,
        "block_to_allow_count": 0,
    }
    return SecondRunDelta(
        delta_id=f"roe15-delta-{result['vertical']}",
        vertical=result["vertical"],
        prior_receipt_ref=result["prior_receipt_ref"],
        new_receipt_ref=result["new_receipt_ref"],
        feedback_ref=result["feedback_id"],
        changed_findings=result.get("finding_updates", []),
        unchanged_findings=result.get("unchanged_findings", []),
        added_fixtures=result.get("fixture_candidates", []),
        added_negative_control_candidates=result.get("negative_control_candidates", []),
        updated_explanations=[item.get("updated_explanation", "") for item in result.get("finding_updates", []) if item.get("updated_explanation")],
        updated_next_actions=result.get("updated_next_actions", []),
        claim_boundary_changes=result.get("claim_boundary_changes", []),
        decision_changes=decision_changes,
        unsafe_decision_upgrade_detected=decision_changes["hold_to_allow_count"] > 0 or decision_changes["block_to_allow_count"] > 0,
        certification_upgrade_detected=bool(result.get("certification_upgrade_detected", False)),
        external_action_authorized=bool(result.get("external_action_authorized", False)),
    )


def delta_to_jsonable(delta: SecondRunDelta) -> dict[str, Any]:
    return delta.model_dump(mode="json", by_alias=True)
