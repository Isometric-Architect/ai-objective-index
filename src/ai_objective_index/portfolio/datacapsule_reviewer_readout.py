from __future__ import annotations

from typing import Any


def build_reviewer_readout_markdown(receipt: dict[str, Any]) -> str:
    manifest = receipt.get("corpus_manifest", {}) if isinstance(receipt.get("corpus_manifest"), dict) else {}
    rights = receipt.get("source_rights_summary", {}) if isinstance(receipt.get("source_rights_summary"), dict) else {}
    privacy = receipt.get("privacy_risk_summary", {}) if isinstance(receipt.get("privacy_risk_summary"), dict) else {}
    eval_summary = receipt.get("eval_leakage_summary", {}) if isinstance(receipt.get("eval_leakage_summary"), dict) else {}
    boundary = receipt.get("use_boundary", {}) if isinstance(receipt.get("use_boundary"), dict) else {}
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
    return f"""# DataCapsule Pilot Reviewer Readout

## What Was Reviewed

- Pilot: `{receipt.get('pilot_id', 'unknown')}`
- Corpus: `{manifest.get('corpus_label', 'unknown')}`
- Source type: `{manifest.get('source_type', 'unknown')}`
- Capsule decision: `{receipt.get('capsule_decision', 'unknown')}`

## Scope

- Local/offline manifest metadata review only.
- Raw corpus content was not inspected.
- No crawling, URL fetching, upload, model training, external API call, or GitHub API call.

## ALLOW/HOLD/BLOCK Summary

| Decision | Count |
| --- | ---: |
| ALLOW | `{summary.get('allow_count', 0)}` |
| HOLD | `{summary.get('hold_count', 0)}` |
| BLOCK | `{summary.get('block_count', 0)}` |

## Source / Rights Summary

- Rights status: `{rights.get('rights_status', 'unknown')}`
- Missing fields: `{', '.join(rights.get('missing_fields', [])) or 'none'}`

## Privacy Risk Summary

- Privacy status: `{privacy.get('privacy_status', 'unknown')}`
- Missing fields: `{', '.join(privacy.get('missing_fields', [])) or 'none'}`

## Evaluation Boundary Summary

- Leakage status: `{eval_summary.get('leakage_status', 'unknown')}`
- Missing fields: `{', '.join(eval_summary.get('missing_fields', [])) or 'none'}`

## Use Boundary

| Use | Decision |
| --- | --- |
| train | `{boundary.get('train_use', 'unknown')}` |
| retrieve | `{boundary.get('retrieve_use', 'unknown')}` |
| evaluate | `{boundary.get('evaluate_use', 'unknown')}` |
| share | `{boundary.get('share_use', 'unknown')}` |
| act | `{boundary.get('act_use', 'unknown')}` |
| commercial | `{boundary.get('commercial_use', 'unknown')}` |

## Findings

| Finding | Decision | Severity | Category | Explanation | Next Action |
| --- | --- | --- | --- | --- | --- |
{finding_table}

## Known Limits

- Not a legal opinion.
- Not a privacy audit.
- Not license clearance.
- Not evaluation-cleanliness proof.
- Not a data quality guarantee.
- No training authorization.
- No action authorization.
"""
