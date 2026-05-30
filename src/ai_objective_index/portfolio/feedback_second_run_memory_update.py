from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class FeedbackSecondRunMemoryUpdate(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackSecondRunMemoryUpdate/v0.1", alias="schema")
    memory_update_id: str
    bridge_id: str
    generated_at: str = Field(default_factory=timestamp)
    updated_entries: list[dict[str, Any]] = Field(default_factory=list)
    portfolio_next_actions: list[str] = Field(default_factory=list)
    external_action_authorized: bool = False


def build_memory_update(
    bridge_id: str,
    executed_results: list[dict[str, Any]],
    skipped_reports: list[dict[str, Any]],
) -> FeedbackSecondRunMemoryUpdate:
    entries: list[dict[str, Any]] = []
    for result in executed_results:
        entries.append(
            {
                "reply_id": result.get("reply_id", ""),
                "vertical": result.get("vertical", ""),
                "prior_status": "second_run_candidate",
                "new_status": "incorporated",
                "incorporation_summary": result.get("incorporation_summary", ""),
                "follow_up_actions": result.get("next_actions", []),
                "fixture_candidate_added": bool(result.get("fixture_candidates")),
                "negative_control_candidate_added": bool(result.get("negative_control_candidates")),
                "claim_boundary_change_needed": False,
            }
        )
    for skipped in skipped_reports:
        entries.append(
            {
                "reply_id": skipped.get("reply_id", skipped.get("candidate_id", "")),
                "vertical": skipped.get("vertical", ""),
                "prior_status": "second_run_candidate",
                "new_status": "skipped_missing_artifact" if skipped.get("reason") == "HOLD_NEEDS_ARTIFACT" else "blocked" if str(skipped.get("reason", "")).startswith("BLOCK_") else "pending_with_followup",
                "incorporation_summary": "candidate skipped because it is not ready for local second-run execution",
                "follow_up_actions": skipped.get("next_actions", []),
                "fixture_candidate_added": False,
                "negative_control_candidate_added": False,
                "claim_boundary_change_needed": False,
            }
        )
    return FeedbackSecondRunMemoryUpdate(
        memory_update_id=f"memory-update-{bridge_id}",
        bridge_id=bridge_id,
        updated_entries=entries,
        portfolio_next_actions=[
            "request artifacts for HOLD candidates",
            "run second pass when local redacted artifacts arrive",
            "keep claim boundaries unchanged",
            "update dashboard in the next package",
        ],
    )


def memory_update_to_jsonable(update: FeedbackSecondRunMemoryUpdate) -> dict[str, Any]:
    return update.model_dump(mode="json", by_alias=True)
