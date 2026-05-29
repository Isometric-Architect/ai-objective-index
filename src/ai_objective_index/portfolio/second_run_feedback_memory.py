from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


NewStatus = Literal["incorporated", "pending_with_followup", "rejected"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class SecondRunFeedbackMemory(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_SecondRunFeedbackMemory/v0.1", alias="schema")
    memory_update_id: str
    second_run_id: str
    generated_at: str = Field(default_factory=timestamp)
    updated_entries: list[dict[str, Any]] = Field(default_factory=list)
    portfolio_next_actions: list[str] = Field(default_factory=list)
    external_action_authorized: bool = False


def build_second_run_feedback_memory(second_run_id: str, vertical_results: list[dict[str, Any]]) -> SecondRunFeedbackMemory:
    entries: list[dict[str, Any]] = []
    for result in vertical_results:
        vertical = result["vertical"]
        new_status: NewStatus = "pending_with_followup" if result.get("requires_followup", False) else "incorporated"
        entries.append(
            {
                "feedback_id": result["feedback_id"],
                "vertical": vertical,
                "prior_status": "pending",
                "new_status": new_status,
                "incorporation_summary": result.get("incorporation_summary", ""),
                "follow_up_actions": result.get("updated_next_actions", []),
                "fixture_candidate_added": bool(result.get("fixture_candidates")),
                "negative_control_candidate_added": bool(result.get("negative_control_candidates")),
                "claim_boundary_change_needed": bool(result.get("claim_boundary_changes")),
            }
        )
    return SecondRunFeedbackMemory(
        memory_update_id=f"second-run-memory-{second_run_id}",
        second_run_id=second_run_id,
        updated_entries=entries,
        portfolio_next_actions=[
            "request owner artifact for a real local pilot",
            "run real owner-consented local pilot only after redaction and consent checks",
            "add second-run dashboard artifact pack",
            "schedule third-run only if unresolved local evidence remains",
        ],
    )


def feedback_memory_to_jsonable(memory: SecondRunFeedbackMemory) -> dict[str, Any]:
    return memory.model_dump(mode="json", by_alias=True)
