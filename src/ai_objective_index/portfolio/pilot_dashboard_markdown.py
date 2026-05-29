from __future__ import annotations

from typing import Any


def build_dashboard_markdown(dashboard: dict[str, Any]) -> str:
    counts = dashboard["aggregate_counts"]
    lines = [
        "# ResidualOps Pilot Dashboard",
        "",
        "Static/local artifact only. This dashboard summarizes local receipt and gate artifacts without network calls or external actions.",
        "",
        "## Lifecycle Summary",
        "",
        "| Stage | Completed |",
        "| --- | --- |",
    ]
    for key, value in dashboard["lifecycle_summary"].items():
        lines.append(f"| {key} | `{value}` |")
    lines.extend(
        [
            "",
            "## Vertical Cards",
            "",
            "| Vertical | Phase | Decision | ALLOW | HOLD | BLOCK | Gate | Feedback |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for card in dashboard["vertical_status_cards"]:
        lines.append(
            f"| {card['display_name']} | `{card['current_phase']}` | `{card['primary_decision']}` | `{card['allow_count']}` | `{card['hold_count']}` | `{card['block_count']}` | `{card['latest_gate_status']}` | `{card['feedback_status']}` |"
        )
    lines.extend(
        [
            "",
            "## ALLOW/HOLD/BLOCK Matrix",
            "",
            f"- Initial: `{counts['initial_allow']}/{counts['initial_hold']}/{counts['initial_block']}`",
            f"- Dry-run: `{counts['dry_run_allow']}/{counts['dry_run_hold']}/{counts['dry_run_block']}`",
            f"- Second-run: `{counts['second_run_allow']}/{counts['second_run_hold']}/{counts['second_run_block']}`",
            "",
            "## Feedback Memory",
            "",
            f"- Feedback entries: `{dashboard['feedback_memory_summary']['entry_count']}`",
            f"- Incorporated: `{dashboard['feedback_memory_summary']['incorporated_count']}`",
            f"- Pending with follow-up: `{dashboard['feedback_memory_summary']['pending_with_followup_count']}`",
            "",
            "## Second-Run Delta Summary",
            "",
            f"- Finding updates: `{counts['finding_updates']}`",
            f"- Fixture candidates: `{counts['fixture_candidates']}`",
            f"- Negative-control candidates: `{counts['negative_control_candidates']}`",
            f"- External actions: `{counts['external_action_count']}`",
            "",
            "## Artifact Index",
            "",
            "| Artifact | Type | Share status |",
            "| --- | --- | --- |",
        ]
    )
    for artifact in dashboard["artifacts"]:
        lines.append(f"| `{artifact['path']}` | `{artifact['artifact_type']}` | `{artifact['safe_to_share_publicly']}` |")
    lines.extend(
        [
            "",
            "## Claim Boundaries",
            "",
            "- Not an external pilot.",
            "- Not security certification.",
            "- Not code correctness proof.",
            "- Not legal, privacy, license, or eval-clean proof.",
            "- Not a quality guarantee.",
            "- Not product readiness.",
            "- No external action authorization.",
            "",
            "## Known Limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in dashboard["known_limits"])
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            f"- Recommended next package: {dashboard['recommended_next_package']}.",
            "- Keep private kernels private and keep any future owner artifact review local/offline unless explicitly approved.",
            "",
        ]
    )
    return "\n".join(lines)
