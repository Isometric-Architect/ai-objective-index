from __future__ import annotations

from typing import Any


def build_reviewer_readout_markdown(receipt: dict[str, Any]) -> str:
    task_packet = receipt.get("task_packet", {}) if isinstance(receipt.get("task_packet"), dict) else {}
    classification = receipt.get("patch_classification", {}) if isinstance(receipt.get("patch_classification"), dict) else {}
    contract = receipt.get("behavior_contract", {}) if isinstance(receipt.get("behavior_contract"), dict) else {}
    ci = receipt.get("ci_evidence_summary", {}) if isinstance(receipt.get("ci_evidence_summary"), dict) else {}
    summary = receipt.get("decision_summary", {}) if isinstance(receipt.get("decision_summary"), dict) else {}
    findings = receipt.get("findings") if isinstance(receipt.get("findings"), list) else []

    rows = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        rows.append(
            "| {id} | {decision} | {severity} | {category} | {explanation} | {next_action} |".format(
                id=finding.get("finding_id", ""),
                decision=finding.get("decision", ""),
                severity=finding.get("severity", ""),
                category=finding.get("category", ""),
                explanation=str(finding.get("explanation", "")).replace("|", "/"),
                next_action=str(finding.get("next_action", "")).replace("|", "/"),
            )
        )
    finding_table = "\n".join(rows) if rows else "| none | HOLD | unknown | unknown | no findings supplied | review manually |"

    expected_behavior = "\n".join(f"- {item}" for item in contract.get("expected_behavior", []))
    return f"""# QIRA Pilot Reviewer Readout

## What Was Reviewed

- Pilot: `{receipt.get('pilot_id', 'unknown')}`
- Task: `{task_packet.get('task_title', 'unknown')}`
- Input source: `{task_packet.get('input_source', 'unknown')}`
- Patch classification: `{classification.get('classification_decision', 'unknown')}`
- CI evidence status: `{ci.get('evidence_status', 'unknown')}`

## Scope

- Local/offline patch review artifact only.
- No GitHub API calls.
- No external repository mutation.
- No merge, deploy, package publish, or PR-comment action.
- No external command execution.

## ALLOW/HOLD/BLOCK Summary

| Decision | Count |
| --- | ---: |
| ALLOW | `{summary.get('allow_count', 0)}` |
| HOLD | `{summary.get('hold_count', 0)}` |
| BLOCK | `{summary.get('block_count', 0)}` |

## Behavior Contract

{expected_behavior}

## Findings

| Finding | Decision | Severity | Category | Explanation | Next Action |
| --- | --- | --- | --- | --- | --- |
{finding_table}

## Known Limits

- Not code correctness proof.
- Not security certification.
- Not a quality guarantee.
- No merge authorization.
- No deploy authorization.
- CI evidence summaries are evidence references, not proof of total correctness.

## Next Actions

- Resolve BLOCK findings before any second-run owner readout.
- Request stronger CI evidence for HOLD findings.
- Keep private calibration and negative-control details outside public artifacts.
"""
