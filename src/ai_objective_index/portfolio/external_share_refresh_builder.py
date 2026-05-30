from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_refresh_checksums import CHECKSUMS_V2_PATH, build_refresh_checksums
from .external_share_refresh_claim_audit import CLAIM_AUDIT_V2_PATH, run_refresh_claim_audit
from .external_share_refresh_delta import build_external_share_refresh_delta, delta_to_jsonable
from .external_share_refresh_distribution_gate import DISTRIBUTION_V2_PATH, run_refresh_distribution_gate
from .external_share_refresh_loader import load_external_share_refresh_sources
from .external_share_refresh_manifest import MANIFEST_V2_PATH, SHARE_V2_DIR, build_refresh_manifest, timestamp
from .external_share_refresh_operator_script import (
    OPERATOR_SCRIPT_V2_PATH,
    SCREENSHOT_SCRIPT_V2_PATH,
    VIDEO_SCRIPT_V2_PATH,
    write_refresh_operator_scripts,
)
from .external_share_refresh_redaction import REDACTION_V2_PATH, scan_refresh_share_artifacts


README_V2_PATH = SHARE_V2_DIR / "README_EXTERNAL_SAFE_DEMO_V2.md"
DEMO_HTML_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html"
DEMO_MD_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.md"
DASHBOARD_JSON_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DASHBOARD_V2.json"
STATUS_CARDS_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_STATUS_CARDS_V2.json"
TIMELINE_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_TIMELINE_V2.json"
FEEDBACK_MEMORY_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_FEEDBACK_MEMORY_V2.json"
CLAIM_BOUNDARY_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_CLAIM_BOUNDARY_V2.md"
KNOWN_LIMITS_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_KNOWN_LIMITS_V2.md"
REFRESH_DELTA_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_REFRESH_DELTA_V2.json"
SHARE_DECISION_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_SHARE_DECISION_V2.md"


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _source_map() -> dict[str, str]:
    return {
        str(DASHBOARD_JSON_V2_PATH).replace("\\", "/"): "pilot_dashboard/ROE21_DASHBOARD_REFRESH_DELTA.json",
        str(STATUS_CARDS_V2_PATH).replace("\\", "/"): "pilot_dashboard/ROE21_FEEDBACK_SECOND_RUN_STATUS_CARDS.json",
        str(TIMELINE_V2_PATH).replace("\\", "/"): "pilot_dashboard/ROE21_FEEDBACK_SECOND_RUN_TIMELINE.json",
        str(FEEDBACK_MEMORY_V2_PATH).replace("\\", "/"): "pilot_dashboard/ROE21_FEEDBACK_SECOND_RUN_MEMORY_SUMMARY.json",
        str(REFRESH_DELTA_V2_PATH).replace("\\", "/"): "pilot_dashboard/ROE21_DASHBOARD_REFRESH_DELTA.json",
    }


def _cards(loaded: dict[str, Any]) -> list[dict[str, Any]]:
    payload = loaded.get("status_cards", {})
    return [card for card in payload.get("cards", []) if isinstance(card, dict)]


def _aggregate_after(loaded: dict[str, Any]) -> dict[str, int]:
    delta = loaded.get("dashboard_refresh_delta", {})
    after = delta.get("aggregate_after", {}) if isinstance(delta, dict) else {}
    return {
        "feedback_bridge_selected_count": int(after.get("feedback_bridge_selected_count", 0) or 0),
        "feedback_bridge_skipped_count": int(after.get("feedback_bridge_skipped_count", 0) or 0),
        "feedback_bridge_executed_count": int(after.get("feedback_bridge_executed_count", 0) or 0),
        "feedback_bridge_allow": int(after.get("feedback_bridge_allow", 0) or 0),
        "feedback_bridge_hold": int(after.get("feedback_bridge_hold", 0) or 0),
        "feedback_bridge_block": int(after.get("feedback_bridge_block", 0) or 0),
        "external_action_count": int(after.get("external_action_count", 0) or 0),
    }


def build_readme() -> str:
    return """# ResidualOps External-Safe Demo Pack V2

This folder is a refreshed static demo/share package generated from the ROE-21 dashboard refresh.

It shows:

- AgentSec feedback second-run: executed and incorporated.
- QIRA: skipped_missing_artifact.
- DataCapsule: skipped_missing_artifact.
- Portfolio: skipped_missing_artifact.
- `external_action_count = 0`.

Use cases:

- internal review;
- investor or partner architecture walkthrough;
- controlled customer discovery with claim ceiling visible;
- bounded screenshot or non-live video with claim ceiling visible.

This is not a product launch, not an external pilot, not security certification, not code correctness proof, not legal/privacy/license/eval-clean proof, not product readiness, not a quality guarantee, and not external action authorization.

No live connector, network dispatch, credentials, raw private data, tokens, private kernels, deploy, publish, merge, upload, training, or external repository mutation is included.
"""


def build_claim_boundary() -> str:
    return """# ResidualOps External-Safe Claim Boundary V2

This V2 share pack is a static local demo artifact.

It is not:

- no external pilot;
- no product launch;
- no security certification;
- no code correctness proof;
- no legal opinion;
- no privacy audit;
- no license clearance;
- no eval-clean proof;
- no quality guarantee;
- no product-readiness claim;
- no external action authorization.

Skipped candidates are HOLD, not success.
"""


def build_known_limits() -> str:
    return """# ResidualOps External-Safe Known Limits V2

- Static/local/offline demo artifacts only.
- No live connector, no network calls, no GitHub API calls, no URL fetching, no crawling, no live MCP/tool calls.
- No raw private-data inspection, no upload, no training, no deploy, no publish, no posting, no merge, no external repository mutation.
- No credentials, tokens, private keys, private kernels, exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, or commercial routing policy.
- Not certification, proof, legal/privacy/license/eval-clean clearance, quality guarantee, product readiness, or action authorization.
- QIRA, DataCapsule, and Portfolio skipped candidates still need local redacted artifacts or clearer context.
"""


def build_share_decision(distribution: dict[str, Any]) -> str:
    return f"""# ResidualOps External-Safe Share Decision V2

Distribution decision: `{distribution['decision']}`

Requested mode: `{distribution['requested_distribution_mode']}`

Allowed current use: local static demo ZIP, internal review, bounded architecture walkthrough, and controlled customer discovery only when the claim ceiling is visible.

Review required before public blog, website teaser, broad recording distribution, partner security questionnaire use, or sandbox connector lab planning.

Blocked: production deployment, live connector demo, external action demo, public auto-posting, live credential use, network dispatch, token/raw PII export, certification claims, legal/privacy compliance claims, product-ready badge, or mutable/rehosted claim surface.
"""


def _status_rows(cards: list[dict[str, Any]]) -> str:
    rows = []
    for card in cards:
        rows.append(
            "| `{vertical}` | `{status}` | `{memory}` | `{allow}/{hold}/{block}` | {next_action} |".format(
                vertical=card.get("vertical", ""),
                status=card.get("feedback_second_run_status", ""),
                memory=card.get("memory_status", ""),
                allow=card.get("latest_decision_summary", {}).get("allow_count", 0),
                hold=card.get("latest_decision_summary", {}).get("hold_count", 0),
                block=card.get("latest_decision_summary", {}).get("block_count", 0),
                next_action=card.get("next_action", ""),
            )
        )
    return "\n".join(rows)


def build_markdown_demo(loaded: dict[str, Any]) -> str:
    after = _aggregate_after(loaded)
    cards = _cards(loaded)
    return f"""# ResidualOps External-Safe Demo V2

Claim ceiling: static local demo only. Not certification, not proof, not product readiness, and no external action authorization.

## Feedback Bridge Summary

- Selected/skipped/executed: `{after['feedback_bridge_selected_count']}/{after['feedback_bridge_skipped_count']}/{after['feedback_bridge_executed_count']}`
- ALLOW/HOLD/BLOCK: `{after['feedback_bridge_allow']}/{after['feedback_bridge_hold']}/{after['feedback_bridge_block']}`
- `external_action_count = {after['external_action_count']}`

## Status Cards

| Vertical | Feedback second-run status | Memory status | ALLOW/HOLD/BLOCK | Next action |
| --- | --- | --- | --- | --- |
{_status_rows(cards)}

Skipped candidates are HOLD, not failure and not success.

## Known Limits

{build_known_limits().splitlines()[2]}

This V2 share pack is regenerated from ROE-21 and replaces the stale ROE-17 share pack for bounded review.
"""


def build_html_demo(loaded: dict[str, Any]) -> str:
    after = _aggregate_after(loaded)
    cards = _cards(loaded)
    row_html = "\n".join(
        "<tr><td>{vertical}</td><td>{status}</td><td>{memory}</td><td>{allow}/{hold}/{block}</td><td>{next}</td></tr>".format(
            vertical=html.escape(str(card.get("vertical", ""))),
            status=html.escape(str(card.get("feedback_second_run_status", ""))),
            memory=html.escape(str(card.get("memory_status", ""))),
            allow=html.escape(str(card.get("latest_decision_summary", {}).get("allow_count", 0))),
            hold=html.escape(str(card.get("latest_decision_summary", {}).get("hold_count", 0))),
            block=html.escape(str(card.get("latest_decision_summary", {}).get("block_count", 0))),
            next=html.escape(str(card.get("next_action", ""))),
        )
        for card in cards
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ResidualOps External-Safe Demo V2</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182026; background: #f7f8f9; }}
    .banner {{ border: 2px solid #1f6feb; background: #eef6ff; padding: 12px; margin-bottom: 18px; }}
    table {{ border-collapse: collapse; width: 100%; background: white; }}
    th, td {{ border: 1px solid #c9d1d9; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f0f3f6; }}
    code {{ background: #eef1f4; padding: 1px 4px; }}
  </style>
</head>
<body>
  <div class="banner"><strong>Claim ceiling:</strong> static local demo only. Not certification, not proof, not product readiness, no external action authorization, no network dependency, and no private kernel exposure.</div>
  <h1>ResidualOps External-Safe Demo V2</h1>
  <p>Generated from the ROE-21 refreshed dashboard. This is a local/offline inspection artifact.</p>
  <h2>Feedback Bridge Summary</h2>
  <ul>
    <li>Selected/skipped/executed: <code>{after['feedback_bridge_selected_count']}/{after['feedback_bridge_skipped_count']}/{after['feedback_bridge_executed_count']}</code></li>
    <li>ALLOW/HOLD/BLOCK: <code>{after['feedback_bridge_allow']}/{after['feedback_bridge_hold']}/{after['feedback_bridge_block']}</code></li>
    <li><code>external_action_count = {after['external_action_count']}</code></li>
  </ul>
  <h2>Status Cards</h2>
  <table>
    <thead><tr><th>Vertical</th><th>Feedback second-run status</th><th>Memory status</th><th>ALLOW/HOLD/BLOCK</th><th>Next action</th></tr></thead>
    <tbody>{row_html}</tbody>
  </table>
  <p><strong>Skipped candidates are HOLD, not failure and not success.</strong></p>
  <h2>Known Limits</h2>
  <p>No live connector, network call, GitHub API call, URL fetch, crawl, live MCP/tool call, raw private-data inspection, upload, training, deploy, publish, posting, merge, external repository mutation, token handling, certification, proof, product-readiness claim, or action authorization.</p>
</body>
</html>
"""


def build_share_pack_payload(loaded: dict[str, Any], manifest: dict[str, Any], distribution: dict[str, Any]) -> dict[str, Any]:
    after = _aggregate_after(loaded)
    return {
        "schema": "ResidualOps_ExternalShareRefresh/v0.1",
        "pack_id": "residualops-external-safe-demo-pack-v2",
        "generated_at": timestamp(),
        "mode": "static_local_redacted_demo_v2",
        "source_dashboard_refresh": "pilot_dashboard/ROE21_DASHBOARD_REFRESH_DELTA.json",
        "status_cards": _cards(loaded),
        "timeline": loaded.get("timeline", {}),
        "feedback_memory": loaded.get("feedback_memory", {}),
        "aggregate_summary": after,
        "included_artifacts": manifest.get("artifacts", []),
        "distribution_boundary": distribution,
        "claim_boundary": {
            "not_external_pilot": True,
            "not_product_launch": True,
            "not_security_certification": True,
            "not_code_correctness_proof": True,
            "not_legal_opinion": True,
            "not_privacy_audit": True,
            "not_license_clearance": True,
            "not_eval_clean_proof": True,
            "not_quality_guarantee": True,
            "not_product_ready": True,
            "no_external_action_authorization": True,
        },
        "skipped_candidates_visible": True,
        "skipped_candidates_marked_success": False,
        "network_used": False,
        "external_actions_performed": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "recommended_next_action": "ROE-23 Manual Feedback Trial Runbook",
    }


def share_refresh_artifact_paths(include_reports: bool = True, include_archive_result: bool = False) -> list[Path]:
    paths = [
        README_V2_PATH,
        DEMO_HTML_V2_PATH,
        DEMO_MD_V2_PATH,
        DASHBOARD_JSON_V2_PATH,
        STATUS_CARDS_V2_PATH,
        TIMELINE_V2_PATH,
        FEEDBACK_MEMORY_V2_PATH,
        CLAIM_BOUNDARY_V2_PATH,
        KNOWN_LIMITS_V2_PATH,
        OPERATOR_SCRIPT_V2_PATH,
        SCREENSHOT_SCRIPT_V2_PATH,
        VIDEO_SCRIPT_V2_PATH,
        REFRESH_DELTA_V2_PATH,
        SHARE_DECISION_V2_PATH,
    ]
    if include_reports:
        paths.extend([MANIFEST_V2_PATH, CHECKSUMS_V2_PATH, REDACTION_V2_PATH, CLAIM_AUDIT_V2_PATH, DISTRIBUTION_V2_PATH])
    if include_archive_result:
        paths.append(SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_ARCHIVE_RESULT_V2.json")
    return paths


def generate_external_share_refresh(write_result: bool = True) -> dict[str, Any]:
    loaded = load_external_share_refresh_sources()
    if loaded["decision"] != "PASS_REFRESHED_DASHBOARD_LOADED":
        return {"source": loaded, "decision": "HOLD_MISSING_REFRESHED_DASHBOARD"}
    if write_result:
        _write_text(README_V2_PATH, build_readme())
        _write_text(DEMO_HTML_V2_PATH, build_html_demo(loaded))
        _write_text(DEMO_MD_V2_PATH, build_markdown_demo(loaded))
        _write_json(STATUS_CARDS_V2_PATH, loaded["status_cards"])
        _write_json(TIMELINE_V2_PATH, loaded["timeline"])
        _write_json(FEEDBACK_MEMORY_V2_PATH, loaded["feedback_memory"])
        _write_text(CLAIM_BOUNDARY_V2_PATH, build_claim_boundary())
        _write_text(KNOWN_LIMITS_V2_PATH, build_known_limits())
        write_refresh_operator_scripts()
        initial_paths = share_refresh_artifact_paths(include_reports=False)
        delta = delta_to_jsonable(build_external_share_refresh_delta(loaded, initial_paths))
        _write_json(REFRESH_DELTA_V2_PATH, delta)
        manifest = build_refresh_manifest(share_refresh_artifact_paths(include_reports=False), source_map=_source_map(), write_result=True)
        checksums = build_refresh_checksums(share_refresh_artifact_paths(include_reports=False) + [MANIFEST_V2_PATH], write_result=True)
        redaction = scan_refresh_share_artifacts(share_refresh_artifact_paths(include_reports=True), write_result=True)
        claim_audit = run_refresh_claim_audit(share_refresh_artifact_paths(include_reports=True), write_result=True)
        distribution = run_refresh_distribution_gate("local_static_demo_zip", write_result=True)
        _write_text(SHARE_DECISION_V2_PATH, build_share_decision(distribution))
        manifest = build_refresh_manifest(share_refresh_artifact_paths(include_reports=True), source_map=_source_map(), write_result=True)
        checksums = build_refresh_checksums(share_refresh_artifact_paths(include_reports=True), write_result=True)
        redaction = scan_refresh_share_artifacts(share_refresh_artifact_paths(include_reports=True), write_result=True)
        claim_audit = run_refresh_claim_audit(share_refresh_artifact_paths(include_reports=True), write_result=True)
        distribution = run_refresh_distribution_gate("local_static_demo_zip", write_result=True)
        _write_json(DASHBOARD_JSON_V2_PATH, build_share_pack_payload(loaded, manifest, distribution))
        manifest = build_refresh_manifest(share_refresh_artifact_paths(include_reports=True), source_map=_source_map(), write_result=True)
        checksums = build_refresh_checksums(share_refresh_artifact_paths(include_reports=True), write_result=True)
        redaction = scan_refresh_share_artifacts(share_refresh_artifact_paths(include_reports=True), write_result=True)
        claim_audit = run_refresh_claim_audit(share_refresh_artifact_paths(include_reports=True), write_result=True)
        distribution = run_refresh_distribution_gate("local_static_demo_zip", write_result=True)
    else:
        delta = {}
        manifest = {"artifact_count": 0, "artifacts": []}
        checksums = {"checksum_count": 0}
        redaction = {"decision": "NOT_WRITTEN"}
        claim_audit = {"decision": "NOT_WRITTEN"}
        distribution = {"decision": "NOT_WRITTEN"}
    return {
        "source": loaded,
        "refresh_delta": _read_json(REFRESH_DELTA_V2_PATH) if write_result else delta,
        "manifest": manifest,
        "checksums": checksums,
        "redaction": redaction,
        "claim_audit": claim_audit,
        "distribution": distribution,
        "share_pack": _read_json(DASHBOARD_JSON_V2_PATH) if write_result else {},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the ROE-22 refreshed external-safe share pack.")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = generate_external_share_refresh(write_result=not args.no_write)
    print(
        "external_share_refresh_builder: "
        f"artifacts={result.get('manifest', {}).get('artifact_count', 0)} "
        f"redaction={result.get('redaction', {}).get('decision', 'UNKNOWN')} "
        f"claim_audit={result.get('claim_audit', {}).get('decision', 'UNKNOWN')} "
        f"distribution={result.get('distribution', {}).get('decision', 'UNKNOWN')}"
    )


if __name__ == "__main__":
    main()
