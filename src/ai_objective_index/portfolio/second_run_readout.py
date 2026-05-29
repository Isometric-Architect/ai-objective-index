from __future__ import annotations

from typing import Any


def build_second_run_readout(receipt: dict[str, Any]) -> str:
    summary = receipt.get("aggregate_summary", {})
    lines = [
        "# ROE-15 Second-Run Reviewer Readout",
        "",
        "ROE-15 executes a local/sample second-run from ROE-14 feedback and second-run plans. It updates explanations, next actions, fixture candidates, and feedback memory without authorizing external actions.",
        "",
        "## Aggregate",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Prior ALLOW/HOLD/BLOCK | `{summary.get('prior_allow_count', 0)}/{summary.get('prior_hold_count', 0)}/{summary.get('prior_block_count', 0)}` |",
        f"| New ALLOW/HOLD/BLOCK | `{summary.get('new_allow_count', 0)}/{summary.get('new_hold_count', 0)}/{summary.get('new_block_count', 0)}` |",
        f"| Finding updates | `{summary.get('finding_updates_count', 0)}` |",
        f"| Fixture candidates | `{summary.get('fixture_candidate_count', 0)}` |",
        f"| Negative-control candidates | `{summary.get('negative_control_candidate_count', 0)}` |",
        f"| External actions | `{summary.get('external_action_count', 0)}` |",
        "",
        "## Vertical Before/After",
        "",
        "| Vertical | Prior | New | Feedback incorporated | Follow-up |",
        "| --- | --- | --- | --- | --- |",
    ]
    memory_entries = {
        entry.get("vertical"): entry
        for entry in receipt.get("feedback_memory_update", {}).get("updated_entries", [])
        if isinstance(entry, dict)
    }
    for result in receipt.get("vertical_results", []):
        prior = result.get("prior_decision_summary", {})
        new = result.get("new_decision_summary", {})
        memory = memory_entries.get(result.get("vertical"), {})
        lines.append(
            "| "
            f"{result.get('vertical', 'unknown')} | "
            f"{prior.get('allow_count', 0)}/{prior.get('hold_count', 0)}/{prior.get('block_count', 0)} | "
            f"{new.get('allow_count', 0)}/{new.get('hold_count', 0)}/{new.get('block_count', 0)} | "
            f"{memory.get('new_status', 'pending')} | "
            f"{'; '.join(memory.get('follow_up_actions', [])[:2])} |"
        )
    lines.extend(
        [
            "",
            "## What Changed",
            "",
        ]
    )
    for delta in receipt.get("deltas", []):
        lines.append(f"### {delta.get('vertical', 'unknown')}")
        if delta.get("changed_findings"):
            lines.append("- Updated finding explanations or next actions.")
        if delta.get("added_fixtures"):
            lines.append("- Added fixture candidate.")
        if delta.get("added_negative_control_candidates"):
            lines.append("- Added negative-control candidate.")
        if not delta.get("changed_findings") and not delta.get("added_fixtures") and not delta.get("added_negative_control_candidates"):
            lines.append("- No decision-changing update.")
        lines.append("")
    lines.extend(
        [
            "## Claim Boundaries",
            "",
            "This is not an external pilot, security certification, code correctness proof, legal/privacy/license/eval-clean proof, quality guarantee, product readiness, or external action authorization.",
            "",
            "## Known Limits",
            "",
            "- Local/sample artifacts only.",
            "- No GitHub API calls, external repository mutation, posting, merge, deploy, package publishing, live MCP/tool calls, external tool execution, upload, model training, or credential use.",
            "- Decision counts are intentionally conservative; ROE-15 prefers explanation and next-action updates over decision upgrades.",
            "",
            "## Next Actions",
            "",
            "- Review incorporated feedback memory entries.",
            "- Request owner-consented local artifacts for a real local pilot.",
            "- Keep private kernels, provider priors, thresholds, private negative controls, private probes, and commercial routing policy non-public.",
        ]
    )
    return "\n".join(lines) + "\n"
