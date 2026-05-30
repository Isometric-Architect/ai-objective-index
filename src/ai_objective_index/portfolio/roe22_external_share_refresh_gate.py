from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_refresh_builder import (
    CLAIM_BOUNDARY_V2_PATH,
    DASHBOARD_JSON_V2_PATH,
    DEMO_HTML_V2_PATH,
    DEMO_MD_V2_PATH,
    KNOWN_LIMITS_V2_PATH,
    README_V2_PATH,
    REFRESH_DELTA_V2_PATH,
    SHARE_DECISION_V2_PATH,
    STATUS_CARDS_V2_PATH,
    generate_external_share_refresh,
)
from .external_share_refresh_checksums import CHECKSUMS_V2_PATH
from .external_share_refresh_claim_audit import CLAIM_AUDIT_V2_PATH
from .external_share_refresh_distribution_gate import DISTRIBUTION_V2_PATH, html_has_network_dependency
from .external_share_refresh_manifest import MANIFEST_V2_PATH
from .external_share_refresh_redaction import REDACTION_V2_PATH


OUTPUT_DIR = Path("public_launch") / "roe22"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE22_EXTERNAL_SHARE_REFRESH_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE22_EXTERNAL_SHARE_REFRESH_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE22_NEXT_ACTIONS.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_text(path: Path) -> str:
    full = _repo_root() / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def _exists(path: Path) -> bool:
    return (_repo_root() / path).exists()


def claim_ceiling_visible() -> bool:
    text = _read_text(DEMO_HTML_V2_PATH).lower()
    return "claim ceiling" in text and "not certification" in text and "no external action authorization" in text


def status_visibility(cards_payload: dict[str, Any]) -> dict[str, Any]:
    cards = [card for card in cards_payload.get("cards", []) if isinstance(card, dict)]
    by_vertical = {card.get("vertical"): card for card in cards}
    false_success = []
    for vertical in ["qira", "datacapsule", "portfolio"]:
        card = by_vertical.get(vertical, {})
        status = str(card.get("feedback_second_run_status", "")).lower()
        memory = str(card.get("memory_status", "")).lower()
        if status != "skipped_missing_artifact":
            false_success.append({"vertical": vertical, "field": "feedback_second_run_status", "value": status})
        if memory != "skipped_missing_artifact":
            false_success.append({"vertical": vertical, "field": "memory_status", "value": memory})
    agentsec = by_vertical.get("agentsec", {})
    return {
        "card_count": len(cards),
        "agentsec_visible": agentsec.get("feedback_second_run_status") == "executed" and agentsec.get("memory_status") == "incorporated",
        "skipped_visible": all(by_vertical.get(vertical, {}).get("feedback_second_run_status") == "skipped_missing_artifact" for vertical in ["qira", "datacapsule", "portfolio"]),
        "false_success": false_success,
    }


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-22 External Share Refresh Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Pack ID | `{result['pack_id']}` |
| Artifacts | `{result['artifact_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim audit | `{result['claim_audit_decision']}` |
| Distribution | `{result['distribution_decision']}` |
| AgentSec visible | `{result['agentsec_executed_incorporated_visible']}` |
| Skipped candidates visible | `{result['skipped_candidates_visible']}` |
| External actions | `{result['external_action_count']}` |

ROE-22 regenerates the external-safe static share pack from ROE-21. It preserves skipped/HOLD candidates and does not authorize external action or make certification/proof/product-readiness claims.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-23 Manual Feedback Trial Runbook" if result["decision"] == "PASS_EXTERNAL_SHARE_PACK_REFRESHED_FROM_UPDATED_DASHBOARD" else "resolve ROE-22 HOLD/BLOCK findings"
    return f"""# ROE-22 Next Actions

Decision: `{result['decision']}`

Recommended next package: {next_step}.

Use the V2 share pack only for bounded review with the claim ceiling visible. Do not deploy, post publicly, run live connectors, use credentials, expose private kernels, hide skipped candidates, or make certification/product-readiness/action-authorization claims.
"""


def run_roe22_gate(write_result: bool = True, ensure_share_refresh: bool = True) -> dict[str, Any]:
    generated = generate_external_share_refresh(write_result=True) if ensure_share_refresh else {}
    share_pack = generated.get("share_pack") if generated else _read_json(DASHBOARD_JSON_V2_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_V2_PATH)
    claim_audit = generated.get("claim_audit") if generated else _read_json(CLAIM_AUDIT_V2_PATH)
    distribution = generated.get("distribution") if generated else _read_json(DISTRIBUTION_V2_PATH)
    manifest = generated.get("manifest") if generated else _read_json(MANIFEST_V2_PATH)
    cards_payload = _read_json(STATUS_CARDS_V2_PATH)
    status = status_visibility(cards_payload)
    required = [
        README_V2_PATH,
        DEMO_HTML_V2_PATH,
        DEMO_MD_V2_PATH,
        DASHBOARD_JSON_V2_PATH,
        STATUS_CARDS_V2_PATH,
        REFRESH_DELTA_V2_PATH,
        CLAIM_BOUNDARY_V2_PATH,
        KNOWN_LIMITS_V2_PATH,
        MANIFEST_V2_PATH,
        CHECKSUMS_V2_PATH,
        REDACTION_V2_PATH,
        CLAIM_AUDIT_V2_PATH,
        DISTRIBUTION_V2_PATH,
        SHARE_DECISION_V2_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    aggregate = share_pack.get("aggregate_summary", {}) if isinstance(share_pack, dict) else {}
    external_action_count = int(aggregate.get("external_action_count", 0) or 0)
    network_dependency = html_has_network_dependency()
    redaction_decision = redaction.get("decision", "UNKNOWN")
    claim_decision = claim_audit.get("decision", "UNKNOWN")
    distribution_decision = distribution.get("decision", "UNKNOWN")
    token_printed = bool(redaction.get("token_printed", False) or share_pack.get("token_printed", False))
    private_kernel = bool(redaction.get("private_kernel_exposed", False) or share_pack.get("private_kernel_exposed", False))

    if generated.get("decision") == "HOLD_MISSING_REFRESHED_DASHBOARD":
        decision = "HOLD_MISSING_REFRESHED_DASHBOARD"
    elif missing:
        decision = "HOLD_MISSING_ARTIFACT"
    elif redaction_decision == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif claim_decision == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
    elif network_dependency:
        decision = "BLOCK_NETWORK_DEPENDENCY"
    elif private_kernel:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif distribution_decision == "HOLD_REVIEW_REQUIRED":
        decision = "HOLD_REVIEW_REQUIRED"
    elif distribution_decision != "PASS_ALLOWED_STATIC_SHARE":
        decision = "BLOCK_UNSAFE_DISTRIBUTION_MODE"
    elif status["false_success"] or not status["skipped_visible"]:
        decision = "BLOCK_SKIPPED_CANDIDATE_FALSE_SUCCESS"
    elif not status["agentsec_visible"]:
        decision = "HOLD_MISSING_REFRESHED_DASHBOARD"
    elif external_action_count != 0:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif not claim_ceiling_visible():
        decision = "HOLD_REVIEW_REQUIRED"
    elif redaction_decision != "PASS_REDACTED":
        decision = "HOLD_REVIEW_REQUIRED"
    else:
        decision = "PASS_EXTERNAL_SHARE_PACK_REFRESHED_FROM_UPDATED_DASHBOARD"

    result = {
        "schema": "ResidualOps_ROE22ExternalShareRefreshGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "pack_id": share_pack.get("pack_id", ""),
        "artifact_count": int(manifest.get("artifact_count", 0) or 0),
        "missing_artifacts": missing,
        "redaction_decision": redaction_decision,
        "redaction_findings": int(redaction.get("finding_count", 0) or 0),
        "claim_audit_decision": claim_decision,
        "claim_audit_findings": int(claim_audit.get("risky_phrase_count", 0) or 0),
        "distribution_decision": distribution_decision,
        "requested_distribution_mode": distribution.get("requested_distribution_mode", ""),
        "network_dependency": network_dependency,
        "claim_ceiling_visible": claim_ceiling_visible(),
        "agentsec_executed_incorporated_visible": bool(status["agentsec_visible"]),
        "skipped_candidates_visible": bool(status["skipped_visible"]),
        "skipped_false_success_findings": status["false_success"],
        "external_action_count": external_action_count,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel,
        "raw_private_data_included": False,
        "external_actions_performed": False,
        "github_api_used": False,
        "live_mcp_call_used": False,
        "can_certify_security": False,
        "can_prove_code_correctness": False,
        "can_provide_legal_privacy_license_eval_proof": False,
        "can_claim_product_readiness": False,
        "can_authorize_external_action": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, _summary_markdown(result))
        _write_text(NEXT_ACTIONS_PATH, _next_actions_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-22 refreshed external-safe share pack gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-share-refresh", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe22_gate(write_result=not args.no_write, ensure_share_refresh=not args.no_share_refresh)
    print(
        "roe22_external_share_refresh_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} "
        f"claim_audit={result['claim_audit_decision']} distribution={result['distribution_decision']}"
    )


if __name__ == "__main__":
    main()
