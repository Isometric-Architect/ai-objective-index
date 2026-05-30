from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .dashboard_refresh_from_feedback import (
    DELTA_PATH,
    MEMORY_SUMMARY_PATH,
    READOUT_PATH,
    STALE_NOTICE_PATH,
    STATUS_CARDS_PATH,
    TIMELINE_PATH,
    dashboard_refresh_artifact_paths,
    refresh_dashboard_from_feedback,
)


OUTPUT_DIR = Path("public_launch") / "roe21"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE21_DASHBOARD_REFRESH_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE21_DASHBOARD_REFRESH_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE21_NEXT_ACTIONS.md"

REFRESH_REDACTION_PATH = Path("pilot_dashboard") / "ROE21_DASHBOARD_REFRESH_REDACTION_REPORT.json"
REFRESH_CLAIM_AUDIT_PATH = Path("pilot_dashboard") / "ROE21_DASHBOARD_REFRESH_CLAIM_AUDIT.json"
SOURCE_HTML_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.html"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _exists(path: Path) -> bool:
    return (_repo_root() / path).exists()


def _has_external_html_dependency(path: Path = SOURCE_HTML_PATH) -> bool:
    full = _repo_root() / path
    if not full.exists():
        return False
    text = full.read_text(encoding="utf-8", errors="ignore").lower()
    return bool(
        re.search(r"<script\b", text)
        or re.search(r"<link\b", text)
        or re.search(r"<form\b", text)
        or "http://" in text
        or "https://" in text
    )


def _skipped_false_success(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for card in cards:
        vertical = card.get("vertical")
        status = str(card.get("feedback_second_run_status", "")).lower()
        memory_status = str(card.get("memory_status", "")).lower()
        if vertical == "agentsec":
            continue
        if "success" in status or status in {"executed", "incorporated", "passed", "pass"}:
            findings.append({"vertical": vertical, "field": "feedback_second_run_status", "value": status})
        if memory_status in {"incorporated", "success", "passed", "pass"}:
            findings.append({"vertical": vertical, "field": "memory_status", "value": memory_status})
        if "skipped" not in status and "hold" not in status and "blocked" not in status:
            findings.append({"vertical": vertical, "field": "feedback_second_run_status", "value": status})
    return findings


def _agentsec_is_executed(cards: list[dict[str, Any]]) -> bool:
    for card in cards:
        if card.get("vertical") == "agentsec":
            return card.get("feedback_second_run_status") == "executed" and card.get("memory_status") == "incorporated"
    return False


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-21 Dashboard Refresh Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Refresh ID | `{result['refresh_id']}` |
| Status cards | `{result['status_card_count']}` |
| Feedback bridge selected/skipped/executed | `{result['feedback_bridge_selected_count']}/{result['feedback_bridge_skipped_count']}/{result['feedback_bridge_executed_count']}` |
| Feedback bridge ALLOW/HOLD/BLOCK | `{result['feedback_bridge_allow']}/{result['feedback_bridge_hold']}/{result['feedback_bridge_block']}` |
| External actions | `{result['external_action_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim audit | `{result['claim_audit_decision']}` |
| External share stale notice | `{result['stale_notice_exists']}` |

ROE-21 refreshes the local/static dashboard after ROE-20. It preserves skipped/HOLD candidates and does not authorize external action or make certification/proof/product-readiness claims.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-22 External Share Pack Refresh from Updated Dashboard" if result["decision"] == "PASS_DASHBOARD_REFRESHED_FROM_FEEDBACK_SECOND_RUN" else "resolve ROE-21 HOLD/BLOCK findings"
    return f"""# ROE-21 Next Actions

Decision: `{result['decision']}`

Recommended next package: {next_step}.

Keep QIRA, DataCapsule, and Portfolio skipped candidates visible until local redacted artifacts or context arrive. Regenerate the external share pack before sharing externally again. Do not post, deploy, call APIs, fetch URLs, run live tools, mutate repositories, upload, train, or make certification/proof/product-readiness claims.
"""


def run_roe21_gate(write_result: bool = True, ensure_refresh: bool = True) -> dict[str, Any]:
    generated = refresh_dashboard_from_feedback(write_result=True) if ensure_refresh else {}
    delta = generated.get("delta") if generated else _read_json(DELTA_PATH)
    status_payload = generated.get("status_cards") if generated else _read_json(STATUS_CARDS_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REFRESH_REDACTION_PATH)
    claim_audit = generated.get("claim_audit") if generated else _read_json(REFRESH_CLAIM_AUDIT_PATH)
    cards = status_payload.get("cards", []) if isinstance(status_payload, dict) else []
    after = delta.get("aggregate_after", {}) if isinstance(delta, dict) else {}
    required = [
        DELTA_PATH,
        STATUS_CARDS_PATH,
        TIMELINE_PATH,
        MEMORY_SUMMARY_PATH,
        READOUT_PATH,
        REFRESH_REDACTION_PATH,
        REFRESH_CLAIM_AUDIT_PATH,
        STALE_NOTICE_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    false_success = _skipped_false_success(cards)
    external_action_count = int(after.get("external_action_count", 0) or 0)
    redaction_decision = redaction.get("decision", "UNKNOWN")
    claim_audit_decision = claim_audit.get("decision", "UNKNOWN")
    token_or_secret = redaction_decision == "BLOCK_SENSITIVE_CONTENT" or bool(redaction.get("token_printed", False))
    private_kernel = bool(redaction.get("private_kernel_exposed", False) or delta.get("private_kernel_exposed", False))
    external_action = external_action_count > 0 or bool(delta.get("no_external_action") is False)
    html_network_dependency = _has_external_html_dependency()

    if missing and any(item.endswith("ROE21_EXTERNAL_SHARE_PACK_STALE_NOTICE.md") for item in missing):
        decision = "HOLD_MISSING_STALE_NOTICE"
    elif missing:
        decision = "HOLD_MISSING_FEEDBACK_SECOND_RUN"
    elif token_or_secret:
        decision = "BLOCK_SECRET_FINDING"
    elif claim_audit_decision != "PASS_CLAIM_BOUNDARY_CLEAN":
        decision = "BLOCK_OVERCLAIM"
    elif external_action:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif private_kernel:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif false_success:
        decision = "BLOCK_SKIPPED_CANDIDATE_FALSE_SUCCESS"
    elif redaction_decision != "PASS_REDACTED":
        decision = "HOLD_REDACTION_REVIEW"
    elif not _agentsec_is_executed(cards):
        decision = "HOLD_MISSING_FEEDBACK_SECOND_RUN"
    elif html_network_dependency:
        decision = "BLOCK_EXTERNAL_ACTION"
    else:
        decision = "PASS_DASHBOARD_REFRESHED_FROM_FEEDBACK_SECOND_RUN"

    result = {
        "schema": "ResidualOps_ROE21DashboardRefreshGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "refresh_id": delta.get("refresh_id", ""),
        "status_card_count": len(cards),
        "feedback_bridge_selected_count": int(after.get("feedback_bridge_selected_count", 0) or 0),
        "feedback_bridge_skipped_count": int(after.get("feedback_bridge_skipped_count", 0) or 0),
        "feedback_bridge_executed_count": int(after.get("feedback_bridge_executed_count", 0) or 0),
        "feedback_bridge_allow": int(after.get("feedback_bridge_allow", 0) or 0),
        "feedback_bridge_hold": int(after.get("feedback_bridge_hold", 0) or 0),
        "feedback_bridge_block": int(after.get("feedback_bridge_block", 0) or 0),
        "external_action_count": external_action_count,
        "missing_artifacts": missing,
        "stale_notice_exists": _exists(STALE_NOTICE_PATH),
        "redaction_decision": redaction_decision,
        "redaction_findings": int(redaction.get("finding_count", 0) or 0),
        "claim_audit_decision": claim_audit_decision,
        "claim_finding_count": int(claim_audit.get("risky_phrase_count", 0) or 0),
        "skipped_false_success_findings": false_success,
        "external_action_used": external_action,
        "html_network_dependency": html_network_dependency,
        "token_printed": bool(redaction.get("token_printed", False)),
        "private_kernel_exposed": private_kernel,
        "github_api_used": False,
        "live_mcp_call_used": False,
        "merge_deploy_publish_performed": False,
        "can_certify_security": False,
        "can_prove_code_correctness": False,
        "can_provide_legal_privacy_license_eval_proof": False,
        "can_claim_product_readiness": False,
        "can_authorize_external_action": False,
        "artifact_paths": [str(path).replace("\\", "/") for path in dashboard_refresh_artifact_paths(include_reports=True)],
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, _summary_markdown(result))
        _write_text(NEXT_ACTIONS_PATH, _next_actions_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-21 dashboard refresh gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-refresh", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe21_gate(write_result=not args.no_write, ensure_refresh=not args.no_refresh)
    print(
        "roe21_dashboard_refresh_gate: "
        f"{result['decision']} selected={result['feedback_bridge_selected_count']} "
        f"skipped={result['feedback_bridge_skipped_count']} executed={result['feedback_bridge_executed_count']} "
        f"redaction={result['redaction_decision']} claim_audit={result['claim_audit_decision']}"
    )


if __name__ == "__main__":
    main()
