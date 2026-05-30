from __future__ import annotations

from typing import Any


def build_feedback_second_run_readout(receipt: dict[str, Any], selection: dict[str, Any]) -> str:
    selected_rows = "\n".join(
        f"| {item.get('vertical', '')} | {item.get('reply_id', '')} | {item.get('primary_decision', '')} | {item.get('new_allow_count', 0)}/{item.get('new_hold_count', 0)}/{item.get('new_block_count', 0)} |"
        for item in receipt.get("selected_results", [])
    )
    skipped_rows = "\n".join(
        f"| {item.get('vertical', '')} | {item.get('candidate_id', '')} | {item.get('reason', '')} | {', '.join(item.get('required_artifacts', []))} |"
        for item in receipt.get("skipped_reports", [])
    )
    summary = receipt.get("aggregate_summary", {})
    return f"""# ROE-20 Feedback Second-Run Bridge Readout

This readout summarizes a local/offline bridge from feedback reply candidates into second-run artifacts.

## Selection Summary

- Source candidates: `{len(selection.get('source_reply_candidates', []))}`
- Selected: `{summary.get('selected_count', 0)}`
- Skipped: `{summary.get('skipped_count', 0)}`
- Executed locally: `{summary.get('executed_count', 0)}`
- External actions: `{summary.get('external_action_count', 0)}`

## Executed Candidate

| Vertical | Reply | Primary decision | ALLOW/HOLD/BLOCK |
| --- | --- | --- | --- |
{selected_rows}

## Skipped Candidates

| Vertical | Candidate | Reason | Required artifacts |
| --- | --- | --- | --- |
{skipped_rows}

## Claim Boundaries

- Not an external pilot.
- Not security certification.
- Not code correctness proof.
- Not legal, privacy, license, or eval-clean proof.
- Not a quality guarantee.
- Not product readiness.
- No external action authorization.

## Known Limits

Only READY local candidates execute. HOLD candidates remain skipped until local redacted artifacts or consent are available. No GitHub API, posting, live MCP/tool call, merge, deploy, publish, upload, training, token use, or repository mutation occurred.

## Next Actions

Request missing local artifacts for skipped candidates, rerun reply intake when they arrive, and refresh the dashboard in the next package.
"""
