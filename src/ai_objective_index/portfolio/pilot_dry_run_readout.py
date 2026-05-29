from __future__ import annotations

from .pilot_dry_run_receipt import PilotDryRunReceipt


def build_dry_run_readout(receipt: PilotDryRunReceipt) -> str:
    summary = receipt.aggregate_summary
    lines = [
        "# ROE-13 Pilot Dry-Run Reviewer Readout",
        "",
        "This readout records a local/sample dry-run from ROE-12 intake packets through local vertical receipt packaging.",
        "",
        "## Route And Receipt Results",
        "",
        "| Vertical | Intake | Receipt | Gate | ALLOW | HOLD | BLOCK | Primary decision | Redaction |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for result in receipt.results:
        lines.append(
            f"| {result.vertical} | `{result.intake_id}` | `{result.receipt_path}` | `{result.gate_result}` | `{result.allow_count}` | `{result.hold_count}` | `{result.block_count}` | `{result.primary_decision}` | `{result.redaction_status}` |"
        )
    lines.extend(
        [
            "",
            "## Aggregate Summary",
            "",
            f"- Verticals: `{summary.get('vertical_count', 0)}`",
            f"- ALLOW: `{summary.get('total_allow_count', 0)}`",
            f"- HOLD: `{summary.get('total_hold_count', 0)}`",
            f"- BLOCK: `{summary.get('total_block_count', 0)}`",
            f"- All redaction passed: `{summary.get('all_redaction_passed', False)}`",
            f"- All gates passed: `{summary.get('all_gates_passed', False)}`",
            f"- External action count: `{summary.get('external_action_count', 0)}`",
            "",
            "## Known Limits",
            "",
            "- Local/sample intake packets only.",
            "- Local/offline vertical packager functions only.",
            "- No external repository, URL, live MCP server, credential, raw private data, upload, training, merge, deploy, publish, or posting action.",
            "",
            "## What This Is Not",
            "",
            "- Not an external pilot.",
            "- Not security certification.",
            "- Not code correctness proof.",
            "- Not legal, privacy, license, or evaluation-cleanliness proof.",
            "- Not a quality guarantee.",
            "- Not product readiness.",
            "- No external action authorization.",
            "",
            "## Next Actions",
            "",
            "- Run a real owner-consented local artifact pilot only after receiving local files or pasted metadata.",
            "- Add a second-run receipt gate.",
            "- Add a unified dashboard.",
            "- Keep AOI MCP Registry recovery as a separate backlog item.",
            "",
        ]
    )
    return "\n".join(lines)
