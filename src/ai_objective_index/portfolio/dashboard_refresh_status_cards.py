from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Vertical = Literal["agentsec", "qira", "datacapsule", "portfolio"]


class DashboardRefreshStatusCard(BaseModel):
    model_config = ConfigDict(extra="allow")

    card_id: str
    vertical: Vertical
    previous_status: str
    feedback_reply_status: str
    feedback_second_run_status: str
    memory_status: str
    latest_decision_summary: dict[str, int] = Field(default_factory=dict)
    next_action: str
    must_not_claim: list[str] = Field(default_factory=list)


def _summary_for_executed(result: dict[str, Any]) -> dict[str, int]:
    summary = result.get("new_decision_summary", {})
    return {
        "allow_count": int(summary.get("allow_count", 0) or 0),
        "hold_count": int(summary.get("hold_count", 0) or 0),
        "block_count": int(summary.get("block_count", 0) or 0),
    }


def _default_must_not_claim() -> list[str]:
    return [
        "security_certification",
        "code_correctness_proof",
        "legal_or_privacy_or_license_or_eval_clean_proof",
        "quality_guarantee",
        "product_readiness",
        "external_action_authorization",
        "skipped_candidate_success",
    ]


def build_dashboard_refresh_status_cards(loaded: dict[str, Any]) -> list[dict[str, Any]]:
    receipt = loaded.get("bridge_receipt", {})
    memory = loaded.get("memory_update", {})
    executed = {item.get("vertical"): item for item in receipt.get("selected_results", []) if isinstance(item, dict)}
    skipped = {item.get("vertical"): item for item in receipt.get("skipped_reports", []) if isinstance(item, dict)}
    memory_entries = {item.get("vertical"): item for item in memory.get("updated_entries", []) if isinstance(item, dict)}
    cards: list[DashboardRefreshStatusCard] = []
    for vertical in ["agentsec", "qira", "datacapsule", "portfolio"]:
        if vertical in executed:
            status = "executed"
            memory_status = str(memory_entries.get(vertical, {}).get("new_status", "incorporated"))
            summary = _summary_for_executed(executed[vertical])
            next_action = "keep local-only AgentSec feedback second-run in dashboard; request owner artifact before any real pilot"
        else:
            skipped_report = skipped.get(vertical, {})
            status = "skipped_missing_artifact" if skipped_report.get("reason") == "HOLD_NEEDS_ARTIFACT" else "hold"
            memory_status = str(memory_entries.get(vertical, {}).get("new_status", "skipped_missing_artifact"))
            summary = {"allow_count": 0, "hold_count": 1, "block_count": 0}
            next_action = "collect a redacted local artifact or context before rerunning; keep this candidate on HOLD"
        cards.append(
            DashboardRefreshStatusCard(
                card_id=f"roe21-status-card-{vertical}",
                vertical=vertical,  # type: ignore[arg-type]
                previous_status="roe16_dashboard_present",
                feedback_reply_status="routed",
                feedback_second_run_status=status,
                memory_status=memory_status,
                latest_decision_summary=summary,
                next_action=next_action,
                must_not_claim=_default_must_not_claim(),
            )
        )
    return [card.model_dump(mode="json") for card in cards]
