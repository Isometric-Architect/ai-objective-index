from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .feedback_second_run_bridge import AGENTSEC_RESULT_PATH
from .feedback_second_run_candidate_selector import SELECTION_REPORT_PATH
from .feedback_second_run_executor import (
    KNOWN_LIMITS_PATH,
    MEMORY_UPDATE_PATH,
    RECEIPT_PATH,
    REVIEWER_READOUT_PATH,
    SKIPPED_DATACAPSULE_PATH,
    SKIPPED_PORTFOLIO_PATH,
    SKIPPED_QIRA_PATH,
    TRACE_PATH,
    run_feedback_second_run_bridge,
)
from .feedback_second_run_redaction import REDACTION_REPORT_PATH


OUTPUT_DIR = Path("public_launch") / "roe20"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_BRIDGE_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_BRIDGE_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE20_NEXT_ACTIONS.md"

RISKY_PATTERNS = [
    re.compile(r"\bsecurity\s+certification\b", re.I),
    re.compile(r"\bcode\s+correctness\s+proof\b", re.I),
    re.compile(r"\blegal\s+clearance\b", re.I),
    re.compile(r"\bprivacy\s+clearance\b", re.I),
    re.compile(r"\blicense\s+clearance\b", re.I),
    re.compile(r"\beval[-\s]+clean\s+proof\b", re.I),
    re.compile(r"\bquality\s+guarantee\b", re.I),
    re.compile(r"\bproduct\s+readiness\b", re.I),
    re.compile(r"\bexternal\s+action\s+authorization\b", re.I),
]
SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "cannot ", "without ", "must not", "claim boundary", "must_not_claim", "known limits"]


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


def scan_feedback_second_run_claims(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if not full.exists() or not full.is_file():
            continue
        lines = full.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            if any(marker in lowered for marker in SAFE_CONTEXT):
                continue
            previous = "\n".join(lines[max(0, line_number - 12) : line_number]).lower()
            if "what this is not" in previous or "claim boundary" in previous or "must_not_claim" in previous or "must not" in previous:
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": str(path).replace("\\", "/"), "line": line_number, "pattern": pattern.pattern})
                    break
    return findings


def _unsafe_upgrade(result: dict[str, Any], receipt: dict[str, Any]) -> bool:
    if result.get("decision_upgrade_performed") or result.get("unsafe_decision_upgrade_detected"):
        return True
    for selected in receipt.get("selected_results", []):
        if selected.get("decision_upgrade_performed") or selected.get("unsafe_decision_upgrade_detected"):
            return True
        changes = selected.get("decision_changes", {})
        if int(changes.get("block_to_allow_count", 0) or 0) > 0:
            return True
        if int(changes.get("hold_to_allow_count", 0) or 0) > 0:
            return True
    return False


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-20 Feedback Second-Run Bridge Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Selected candidates | `{result['selected_count']}` |
| Skipped candidates | `{result['skipped_count']}` |
| Executed candidates | `{result['executed_count']}` |
| New ALLOW/HOLD/BLOCK | `{result['new_allow_count']}/{result['new_hold_count']}/{result['new_block_count']}` |
| Redaction | `{result['redaction_decision']}` |
| External actions | `{result['external_action_count']}` |

ROE-20 is a local feedback-to-second-run bridge. It is not an external pilot, certification, proof, product readiness, quality guarantee, or action authorization.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-21 Dashboard Refresh from Feedback Second-Run" if result["decision"] == "PASS_FEEDBACK_TO_SECOND_RUN_BRIDGE_READY" else "resolve ROE-20 HOLD/BLOCK findings"
    return f"""# ROE-20 Next Actions

Decision: `{result['decision']}`

Recommended next package: {next_step}.

Keep skipped candidates on HOLD until local redacted artifacts or clearer context arrive. Do not create issues, post comments, call APIs, fetch URLs, run live MCP/tool calls, mutate repositories, merge, deploy, publish, upload, train, use credentials, or make certification/proof/product-readiness claims.
"""


def run_roe20_gate(write_result: bool = True, ensure_bridge: bool = True) -> dict[str, Any]:
    generated = run_feedback_second_run_bridge(sample=True, write_result=True) if ensure_bridge else {}
    receipt = generated.get("receipt") if generated else _read_json(RECEIPT_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    trace = generated.get("trace") if generated else _read_json(TRACE_PATH)
    selected_result = (generated.get("selected_results") or [_read_json(AGENTSEC_RESULT_PATH)])[0] if generated.get("selected_results") or _read_json(AGENTSEC_RESULT_PATH) else {}
    required = [
        SELECTION_REPORT_PATH,
        TRACE_PATH,
        RECEIPT_PATH,
        AGENTSEC_RESULT_PATH,
        SKIPPED_QIRA_PATH,
        SKIPPED_DATACAPSULE_PATH,
        SKIPPED_PORTFOLIO_PATH,
        MEMORY_UPDATE_PATH,
        REVIEWER_READOUT_PATH,
        REDACTION_REPORT_PATH,
        KNOWN_LIMITS_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    claim_findings = scan_feedback_second_run_claims(required + [Path("docs") / "portfolio" / "feedback_second_run_claim_boundaries.md"])
    summary = receipt.get("aggregate_summary", {}) if isinstance(receipt, dict) else {}
    selected_count = int(summary.get("selected_count", 0) or 0)
    skipped_count = int(summary.get("skipped_count", 0) or 0)
    executed_count = int(summary.get("executed_count", 0) or 0)
    external_action_count = int(summary.get("external_action_count", 0) or 0)
    external_action = bool(
        external_action_count
        or receipt.get("external_actions_performed", False)
        or trace.get("external_network_used", False)
        or trace.get("github_api_used", False)
        or trace.get("live_mcp_call_used", False)
        or trace.get("external_repo_modified", False)
        or trace.get("posting_or_commenting_performed", False)
        or trace.get("merge_deploy_publish_performed", False)
    )
    token_printed = bool(redaction.get("token_printed", False) or trace.get("token_used", False) or selected_result.get("token_used", False))
    private_kernel_exposed = bool(redaction.get("private_kernel_exposed", False) or receipt.get("private_kernel_exposed", False))
    unsafe_upgrade = _unsafe_upgrade(selected_result, receipt)

    if selected_count == 0:
        decision = "HOLD_NO_READY_CANDIDATES"
    elif missing and any("SKIPPED" in item for item in missing):
        decision = "HOLD_MISSING_SKIPPED_REPORT"
    elif missing:
        decision = "HOLD_MISSING_SKIPPED_REPORT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif claim_findings:
        decision = "BLOCK_OVERCLAIM"
    elif external_action:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif unsafe_upgrade:
        decision = "BLOCK_UNSAFE_DECISION_UPGRADE"
    elif private_kernel_exposed:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif redaction.get("decision") != "PASS_REDACTED":
        decision = "HOLD_REDACTION_REVIEW"
    elif executed_count != selected_count:
        decision = "HOLD_NO_READY_CANDIDATES"
    elif skipped_count < 1:
        decision = "HOLD_MISSING_SKIPPED_REPORT"
    else:
        decision = "PASS_FEEDBACK_TO_SECOND_RUN_BRIDGE_READY"

    result = {
        "schema": "ResidualOps_ROE20FeedbackSecondRunBridgeGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "bridge_id": receipt.get("bridge_id", ""),
        "selected_count": selected_count,
        "skipped_count": skipped_count,
        "executed_count": executed_count,
        "new_allow_count": int(summary.get("new_allow_count", 0) or 0),
        "new_hold_count": int(summary.get("new_hold_count", 0) or 0),
        "new_block_count": int(summary.get("new_block_count", 0) or 0),
        "finding_updates_count": int(summary.get("finding_updates_count", 0) or 0),
        "fixture_candidate_count": int(summary.get("fixture_candidate_count", 0) or 0),
        "negative_control_candidate_count": int(summary.get("negative_control_candidate_count", 0) or 0),
        "external_action_count": external_action_count,
        "missing_artifacts": missing,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": int(redaction.get("finding_count", 0) or 0),
        "claim_finding_count": len(claim_findings),
        "claim_findings": claim_findings[:50],
        "external_action_used": external_action,
        "unsafe_decision_upgrade_detected": unsafe_upgrade,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel_exposed,
        "github_api_used": bool(trace.get("github_api_used", False)),
        "live_mcp_call_used": bool(trace.get("live_mcp_call_used", False)),
        "merge_deploy_publish_performed": bool(trace.get("merge_deploy_publish_performed", False)),
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
    parser = argparse.ArgumentParser(description="Run the ROE-20 feedback-to-second-run bridge gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-bridge", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe20_gate(write_result=not args.no_write, ensure_bridge=not args.no_bridge)
    print(
        "roe20_feedback_second_run_bridge_gate: "
        f"{result['decision']} selected={result['selected_count']} skipped={result['skipped_count']} "
        f"executed={result['executed_count']} redaction={result['redaction_decision']}"
    )


if __name__ == "__main__":
    main()
