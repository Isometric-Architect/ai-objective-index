from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_dashboard_builder import (
    CHECKSUMS_PATH,
    CLAIM_BOUNDARY_PATH,
    DASHBOARD_HTML_PATH,
    DASHBOARD_JSON_PATH,
    DASHBOARD_MD_PATH,
    KNOWN_LIMITS_PATH,
    MANIFEST_PATH,
    STATUS_CARDS_PATH,
    TIMELINE_PATH,
    generate_dashboard,
)
from .pilot_dashboard_claim_audit import run_dashboard_claim_audit
from .pilot_dashboard_redaction import REDACTION_REPORT_PATH


OUTPUT_DIR = Path("public_launch") / "roe16"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE16_DASHBOARD_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE16_DASHBOARD_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE16_NEXT_ACTIONS.md"


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


def html_has_external_dependency(path: Path = DASHBOARD_HTML_PATH) -> bool:
    full = _repo_root() / path
    if not full.exists():
        return False
    text = full.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"<script\b", text, re.I):
        return True
    if re.search(r"<link\b", text, re.I):
        return True
    if re.search(r"<form\b", text, re.I):
        return True
    if re.search(r"https?://", text, re.I):
        return True
    return False


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-16 Dashboard Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Dashboard ID | `{result['dashboard_id']}` |
| Status cards | `{result['status_card_count']}` |
| Second-run ALLOW/HOLD/BLOCK | `{result['second_run_allow']}/{result['second_run_hold']}/{result['second_run_block']}` |
| Dashboard artifacts | `{result['artifact_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim audit | `{result['claim_audit_decision']}` |
| External action count | `{result['external_action_count']}` |

ROE-16 is a static/local dashboard artifact pack. It does not perform external actions and does not certify security, prove correctness, provide legal/privacy/license/eval-clean proof, guarantee quality, claim product readiness, or authorize actions.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-17 External-Safe Demo/Share Pack" if result["decision"] == "PASS_PILOT_DASHBOARD_ARTIFACT_READY" else "resolve ROE-16 HOLD/BLOCK findings"
    return f"""# ROE-16 Next Actions

Decision: `{result['decision']}`

Recommended next package: {next_step}.

Keep the dashboard static/local unless a later package explicitly creates a share pack with redaction and claim-boundary gates. Do not add external scripts, forms, API calls, posting, publishing, deployment, or certification/product-readiness claims.
"""


def run_roe16_gate(write_result: bool = True, ensure_dashboard: bool = True) -> dict[str, Any]:
    generated = generate_dashboard(write_result=True) if ensure_dashboard else {}
    dashboard = generated.get("dashboard") if generated else _read_json(DASHBOARD_JSON_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    claim_audit = generated.get("claim_audit") if generated else run_dashboard_claim_audit(write_result=write_result)
    manifest = generated.get("manifest") if generated else _read_json(MANIFEST_PATH)
    required = [
        DASHBOARD_JSON_PATH,
        DASHBOARD_MD_PATH,
        DASHBOARD_HTML_PATH,
        MANIFEST_PATH,
        CHECKSUMS_PATH,
        STATUS_CARDS_PATH,
        TIMELINE_PATH,
        CLAIM_BOUNDARY_PATH,
        REDACTION_REPORT_PATH,
        KNOWN_LIMITS_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not (_repo_root() / path).exists()]
    gate_status = dashboard.get("gate_status", {}) if isinstance(dashboard, dict) else {}
    prior_gates = {key: value for key, value in gate_status.items() if key != "dashboard_gate"}
    missing_prior_gate = [key for key, value in prior_gates.items() if not str(value).startswith("PASS_")]
    external_action_count = int(dashboard.get("aggregate_counts", {}).get("external_action_count", 0) or dashboard.get("external_action_count", 0) or 0)
    external_dependency = html_has_external_dependency()
    token_printed = bool(redaction.get("token_printed", False) or dashboard.get("token_printed", False))
    private_kernel_exposed = bool(redaction.get("private_kernel_exposed", False) or dashboard.get("private_kernel_exposed", False))

    if missing:
        decision = "HOLD_MISSING_ARTIFACT"
    elif missing_prior_gate:
        decision = "HOLD_MISSING_PRIOR_GATE"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_audit.get("decision") == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
    elif external_dependency:
        decision = "BLOCK_EXTERNAL_NETWORK_DEPENDENCY"
    elif external_action_count:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif private_kernel_exposed:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    else:
        decision = "PASS_PILOT_DASHBOARD_ARTIFACT_READY"

    result = {
        "schema": "ResidualOps_ROE16DashboardGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "dashboard_id": dashboard.get("dashboard_id", ""),
        "status_card_count": len(dashboard.get("vertical_status_cards", [])) if isinstance(dashboard, dict) else 0,
        "second_run_allow": int(dashboard.get("aggregate_counts", {}).get("second_run_allow", 0) or 0),
        "second_run_hold": int(dashboard.get("aggregate_counts", {}).get("second_run_hold", 0) or 0),
        "second_run_block": int(dashboard.get("aggregate_counts", {}).get("second_run_block", 0) or 0),
        "artifact_count": int(manifest.get("artifact_count", 0) or 0),
        "missing_artifacts": missing,
        "missing_prior_gates": missing_prior_gate,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": int(redaction.get("finding_count", 0) or 0),
        "claim_audit_decision": claim_audit.get("decision", "UNKNOWN"),
        "claim_audit_findings": int(claim_audit.get("risky_phrase_count", 0) or 0),
        "external_html_dependency": external_dependency,
        "external_action_count": external_action_count,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel_exposed,
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
    parser = argparse.ArgumentParser(description="Run the ROE-16 pilot dashboard artifact gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-dashboard", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe16_gate(write_result=not args.no_write, ensure_dashboard=not args.no_dashboard)
    print(
        "roe16_dashboard_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} "
        f"claim_audit={result['claim_audit_decision']} artifacts={result['artifact_count']}"
    )


if __name__ == "__main__":
    main()
