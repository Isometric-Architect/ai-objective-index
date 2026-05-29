from __future__ import annotations

from typing import Any


def build_reviewer_readout_markdown(receipt: dict[str, Any]) -> str:
    summary = receipt.get("decision_summary", {}) if isinstance(receipt.get("decision_summary"), dict) else {}
    packet = receipt.get("packet_summary", {}) if isinstance(receipt.get("packet_summary"), dict) else {}
    findings = receipt.get("findings", []) if isinstance(receipt.get("findings"), list) else []
    rows = "\n".join(
        "| `{id}` | `{decision}` | `{category}` | `{severity}` | {next_action} |".format(
            id=finding.get("finding_id", "unknown"),
            decision=finding.get("decision", "HOLD"),
            category=finding.get("category", "unknown"),
            severity=finding.get("severity", "unknown"),
            next_action=str(finding.get("next_action", "review")).replace("|", "/"),
        )
        for finding in findings
        if isinstance(finding, dict)
    )
    if not rows:
        rows = "| `none` | `ALLOW` | `unknown` | `info` | No finding cards recorded. |"
    return f"""# AgentSec Pilot Reviewer Readout

Pilot: `{receipt.get('pilot_id', 'unknown')}`

Project: `{receipt.get('project_label', 'unknown')}`

## Scope

- Manifest-only review: `{receipt.get('review_scope', {}).get('manifest_only', True)}`
- Live MCP call: `False`
- Live tool execution: `False`
- GitHub API call: `False`
- External network: `False`

## Summary

| Field | Value |
| --- | --- |
| Manifests | `{packet.get('manifest_count', 0)}` |
| Tools | `{packet.get('tool_count', 0)}` |
| Permissions | `{packet.get('permission_count', 0)}` |
| ALLOW | `{summary.get('allow_count', 0)}` |
| HOLD | `{summary.get('hold_count', 0)}` |
| BLOCK | `{summary.get('block_count', 0)}` |

## Findings

| Finding | Decision | Category | Severity | Next Action |
| --- | --- | --- | --- | --- |
{rows}

## Known Limits

- This is a local/offline manifest review artifact.
- It is not security certification.
- It is not a compliance audit.
- It is not a quality guarantee.
- It is not a live exploit scan.
- It is not production-readiness proof.
- It does not authorize external actions.
"""
