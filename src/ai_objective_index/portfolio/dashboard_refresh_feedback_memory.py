from __future__ import annotations

from typing import Any


def build_dashboard_refresh_feedback_memory_summary(loaded: dict[str, Any]) -> dict[str, Any]:
    memory = loaded.get("memory_update", {})
    entries = [entry for entry in memory.get("updated_entries", []) if isinstance(entry, dict)]
    normalized = []
    for entry in entries:
        normalized.append(
            {
                "vertical": entry.get("vertical", "unknown"),
                "reply_id": entry.get("reply_id", ""),
                "new_status": entry.get("new_status", "unknown"),
                "follow_up_actions": entry.get("follow_up_actions", []),
                "fixture_candidate_added": bool(entry.get("fixture_candidate_added", False)),
                "claim_boundary_change_needed": bool(entry.get("claim_boundary_change_needed", False)),
            }
        )
    return {
        "schema": "ResidualOps_DashboardRefreshFeedbackSummary/v0.1",
        "entry_count": len(normalized),
        "incorporated_count": len([entry for entry in normalized if entry["new_status"] == "incorporated"]),
        "skipped_missing_artifact_count": len([entry for entry in normalized if entry["new_status"] == "skipped_missing_artifact"]),
        "pending_with_followup_count": len([entry for entry in normalized if entry["new_status"] == "pending_with_followup"]),
        "entries": normalized,
        "external_action_authorized": False,
    }
