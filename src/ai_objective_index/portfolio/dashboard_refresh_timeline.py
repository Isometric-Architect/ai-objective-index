from __future__ import annotations

from typing import Any


def build_dashboard_refresh_timeline(loaded: dict[str, Any]) -> dict[str, Any]:
    prior_events = loaded.get("source_timeline", {}).get("events", [])
    receipt = loaded.get("bridge_receipt", {})
    summary = receipt.get("aggregate_summary", {}) if isinstance(receipt, dict) else {}
    events = [event for event in prior_events if isinstance(event, dict)]
    events.append(
        {
            "phase": "feedback_second_run_bridge",
            "artifact": "ROE-20 local feedback-to-second-run bridge",
            "decision": "PASS_FEEDBACK_TO_SECOND_RUN_BRIDGE_READY",
            "selected_count": int(summary.get("selected_count", 0) or 0),
            "skipped_count": int(summary.get("skipped_count", 0) or 0),
            "executed_count": int(summary.get("executed_count", 0) or 0),
            "external_action_count": int(summary.get("external_action_count", 0) or 0),
        }
    )
    events.append(
        {
            "phase": "dashboard_refresh",
            "artifact": "ROE-21 dashboard refresh artifacts",
            "decision": "GENERATED",
            "external_action_count": 0,
        }
    )
    return {"schema": "ResidualOps_DashboardRefreshTimeline/v0.1", "event_count": len(events), "events": events}
