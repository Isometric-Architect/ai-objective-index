from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class DashboardRefreshDelta(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_DashboardRefreshDelta/v0.1", alias="schema")
    refresh_id: str
    generated_at: str = Field(default_factory=timestamp)
    source_dashboard_ref: str
    source_feedback_second_run_ref: str
    previous_dashboard_phase: str = "roe16_dashboard"
    new_dashboard_phase: str = "roe21_feedback_second_run_refreshed"
    updates: list[str] = Field(default_factory=list)
    aggregate_before: dict[str, int] = Field(default_factory=dict)
    aggregate_after: dict[str, int] = Field(default_factory=dict)
    claim_boundary_unchanged: bool = True
    no_external_action: bool = True


def build_dashboard_refresh_delta(loaded: dict[str, Any]) -> DashboardRefreshDelta:
    source_dashboard = loaded.get("source_dashboard", {})
    receipt = loaded.get("bridge_receipt", {})
    before_counts = source_dashboard.get("aggregate_counts", {}) if isinstance(source_dashboard, dict) else {}
    after_counts = receipt.get("aggregate_summary", {}) if isinstance(receipt, dict) else {}
    return DashboardRefreshDelta(
        refresh_id="roe21-dashboard-refresh-v0-1",
        source_dashboard_ref="pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.json",
        source_feedback_second_run_ref="feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_RECEIPT.json",
        updates=[
            "agentsec_feedback_second_run_status",
            "qira_skipped_status",
            "datacapsule_skipped_status",
            "portfolio_skipped_status",
            "feedback_memory_updates",
            "timeline_updates",
            "external_share_pack_stale_notice",
        ],
        aggregate_before={
            "dashboard_vertical_count": len(source_dashboard.get("verticals", [])) if isinstance(source_dashboard, dict) else 0,
            "second_run_allow": int(before_counts.get("second_run_allow", 0) or 0),
            "second_run_hold": int(before_counts.get("second_run_hold", 0) or 0),
            "second_run_block": int(before_counts.get("second_run_block", 0) or 0),
        },
        aggregate_after={
            "feedback_bridge_selected_count": int(after_counts.get("selected_count", 0) or 0),
            "feedback_bridge_skipped_count": int(after_counts.get("skipped_count", 0) or 0),
            "feedback_bridge_executed_count": int(after_counts.get("executed_count", 0) or 0),
            "feedback_bridge_allow": int(after_counts.get("new_allow_count", 0) or 0),
            "feedback_bridge_hold": int(after_counts.get("new_hold_count", 0) or 0),
            "feedback_bridge_block": int(after_counts.get("new_block_count", 0) or 0),
            "external_action_count": int(after_counts.get("external_action_count", 0) or 0),
        },
    )


def delta_to_jsonable(delta: DashboardRefreshDelta) -> dict[str, Any]:
    return delta.model_dump(mode="json", by_alias=True)
