from __future__ import annotations

from typing import Any


def build_dashboard_refresh_readout(delta: dict[str, Any], cards: list[dict[str, Any]], memory_summary: dict[str, Any]) -> str:
    after = delta.get("aggregate_after", {})
    lines = [
        "# ROE-21 Dashboard Refresh Readout",
        "",
        "ROE-21 refreshes the static/local ResidualOps dashboard from the ROE-20 feedback-to-second-run bridge.",
        "",
        "## What Changed Since ROE-16",
        "",
        "- Added ROE-20 feedback bridge status.",
        "- Added AgentSec executed/incorporated feedback second-run status.",
        "- Preserved QIRA, DataCapsule, and Portfolio skipped/HOLD status.",
        "- Marked the ROE-17 external share pack stale until regenerated.",
        "",
        "## ROE-20 Bridge Summary",
        "",
        f"- Selected candidates: `{after.get('feedback_bridge_selected_count', 0)}`",
        f"- Skipped candidates: `{after.get('feedback_bridge_skipped_count', 0)}`",
        f"- Executed candidates: `{after.get('feedback_bridge_executed_count', 0)}`",
        f"- ALLOW/HOLD/BLOCK for executed feedback bridge result: `{after.get('feedback_bridge_allow', 0)}/{after.get('feedback_bridge_hold', 0)}/{after.get('feedback_bridge_block', 0)}`",
        f"- External actions: `{after.get('external_action_count', 0)}`",
        "",
        "## Status Cards",
        "",
        "| Vertical | Feedback second-run status | Memory status | Next action |",
        "| --- | --- | --- | --- |",
    ]
    for card in cards:
        lines.append(f"| `{card['vertical']}` | `{card['feedback_second_run_status']}` | `{card['memory_status']}` | {card['next_action']} |")
    lines.extend(
        [
            "",
            "## Skipped Candidates",
            "",
            "Skipped candidates are not failures and not successes. They remain HOLD until a redacted local artifact, clearer context, or consent is available.",
            "",
            "## Feedback Memory",
            "",
            f"- Entries: `{memory_summary['entry_count']}`",
            f"- Incorporated: `{memory_summary['incorporated_count']}`",
            f"- Skipped missing artifact: `{memory_summary['skipped_missing_artifact_count']}`",
            "",
            "## External Share Pack Staleness",
            "",
            "The ROE-17 external share pack was valid at creation time, but it does not include ROE-20 feedback bridge state. Regenerate the share pack before bounded external sharing.",
            "",
            "## What This Is Not",
            "",
            "- Not a product update.",
            "- Not an external action.",
            "- Not certification.",
            "- Not code correctness proof.",
            "- Not legal, privacy, license, or eval-clean proof.",
            "- No action authorization.",
            "",
            "## Next Actions",
            "",
            "- ROE-22 External Share Pack Refresh from Updated Dashboard.",
            "- Keep skipped candidates visible and unresolved until local artifacts arrive.",
            "",
        ]
    )
    return "\n".join(lines)
