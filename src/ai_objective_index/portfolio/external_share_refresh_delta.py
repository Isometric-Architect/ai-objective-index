from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class ExternalShareRefreshDelta(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_ExternalShareRefreshDelta/v0.1", alias="schema")
    refresh_id: str
    generated_at: str = Field(default_factory=timestamp)
    source_previous_share_pack: str = "external_share_pack"
    source_dashboard_refresh: str = "pilot_dashboard/ROE21_DASHBOARD_REFRESH_DELTA.json"
    previous_share_pack_status: str = "stale"
    new_share_pack_status: str = "refreshed_from_roe21"
    updates: list[str] = Field(default_factory=list)
    removed_or_deprecated_artifacts: list[str] = Field(default_factory=list)
    newly_generated_artifacts: list[str] = Field(default_factory=list)
    claim_boundary_unchanged: bool = True
    no_external_action: bool = True


def build_external_share_refresh_delta(loaded: dict[str, Any], generated_artifacts: list[Path] | None = None) -> ExternalShareRefreshDelta:
    previous_manifest = loaded.get("previous_share_manifest", {})
    previous_artifacts = [
        str(item.get("path", ""))
        for item in previous_manifest.get("artifacts", [])
        if isinstance(item, dict) and item.get("path")
    ]
    new_artifacts = [str(path).replace("\\", "/") for path in (generated_artifacts or [])]
    return ExternalShareRefreshDelta(
        refresh_id="roe22-external-share-refresh-v0-1",
        updates=[
            "agentsec_feedback_second_run_executed",
            "qira_skipped_missing_artifact_visible",
            "datacapsule_skipped_missing_artifact_visible",
            "portfolio_skipped_missing_artifact_visible",
            "external_action_count_zero",
            "claim_ceiling_visible",
            "stale_notice_replaced_by_v2",
        ],
        removed_or_deprecated_artifacts=previous_artifacts,
        newly_generated_artifacts=new_artifacts,
    )


def delta_to_jsonable(delta: ExternalShareRefreshDelta) -> dict[str, Any]:
    return delta.model_dump(mode="json", by_alias=True)
