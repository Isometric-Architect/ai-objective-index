from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_dry_run import (
    DATACAPSULE_RESULT_PATH,
    FEEDBACK_MEMORY_PATH,
    KNOWN_LIMITS_PATH,
    QIRA_RESULT_PATH,
    RECEIPT_PATH,
    REVIEWER_READOUT_PATH,
    TRACE_PATH,
    run_pilot_dry_run,
)
from .pilot_dry_run_executor import AGENTSEC_RESULT_PATH
from .pilot_dry_run_redaction import REDACTION_REPORT_PATH


OUTPUT_DIR = Path("public_launch") / "roe13"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE13_PILOT_DRY_RUN_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE13_PILOT_DRY_RUN_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE13_NEXT_ACTIONS.md"

RISKY_PATTERNS = [
    re.compile(r"\bsecurity\s+certification\b", re.I),
    re.compile(r"\bcorrectness\s+proof\b", re.I),
    re.compile(r"\blegal\s+clearance\b", re.I),
    re.compile(r"\bprivacy\s+clearance\b", re.I),
    re.compile(r"\blicense\s+clearance\b", re.I),
    re.compile(r"\beval[-\s]+clean\s+proof\b", re.I),
    re.compile(r"\bquality\s+guarantee\b", re.I),
    re.compile(r"\bproduct\s+readiness\b", re.I),
    re.compile(r"\bexternal\s+action\s+authorization\b", re.I),
]
SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "cannot ", "without ", "must not", "known limits", "claim boundary"]


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


def _exists(path: Path) -> bool:
    return (_repo_root() / path).exists()


def scan_dry_run_claims(paths: list[Path]) -> list[dict[str, Any]]:
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
            previous = "\n".join(lines[max(0, line_number - 5) : line_number]).lower()
            if "what this is not" in previous or "must_not_claim" in previous or "claim boundary" in previous:
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": str(path).replace("\\", "/"), "line": line_number, "pattern": pattern.pattern})
                    break
    return findings


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-13 Pilot Dry-Run Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Verticals | `{result['vertical_count']}` |
| ALLOW | `{result['total_allow_count']}` |
| HOLD | `{result['total_hold_count']}` |
| BLOCK | `{result['total_block_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim findings | `{result['claim_finding_count']}` |
| External action used | `{result['external_action_used']}` |

This is a local/sample flow artifact. It is not an external pilot, certification, proof, product readiness, quality guarantee, or action authorization.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-14 Pilot Feedback Form + Second-Run Receipt Gate" if result["decision"] == "PASS_FIRST_OWNER_CONSENTED_PILOT_DRY_RUN_READY" else "resolve ROE-13 HOLD/BLOCK findings"
    return f"""# ROE-13 Next Actions

Decision: `{result['decision']}`

Recommended next step: {next_step}.

Keep the same limits: use local files only, confirm owner consent, run redaction, avoid credentials, and do not post, merge, deploy, upload, train, fetch, clone, call external APIs, call live MCP/tool servers, or make certification/proof/product-readiness claims.
"""


def run_roe13_gate(write_result: bool = True, ensure_dry_run: bool = True) -> dict[str, Any]:
    generated = run_pilot_dry_run(sample=True, write_result=True) if ensure_dry_run else {}
    receipt = generated.get("receipt") if generated else _read_json(RECEIPT_PATH)
    trace = generated.get("trace") if generated else _read_json(TRACE_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    required = [
        RECEIPT_PATH,
        TRACE_PATH,
        AGENTSEC_RESULT_PATH,
        QIRA_RESULT_PATH,
        DATACAPSULE_RESULT_PATH,
        REVIEWER_READOUT_PATH,
        FEEDBACK_MEMORY_PATH,
        REDACTION_REPORT_PATH,
        KNOWN_LIMITS_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    claim_findings = scan_dry_run_claims(required + [Path("docs") / "portfolio" / "pilot_dry_run_claim_boundaries.md"])
    summary = receipt.get("aggregate_summary", {}) if isinstance(receipt, dict) else {}
    expected_verticals = {"agentsec", "qira", "datacapsule"}
    executed_verticals = set(trace.get("executed_verticals", [])) if isinstance(trace, dict) else set()
    external_action_used = bool(
        trace.get("external_network_used", False)
        or trace.get("github_api_used", False)
        or trace.get("live_mcp_call_used", False)
        or trace.get("external_repo_modified", False)
        or trace.get("posting_or_commenting_performed", False)
        or trace.get("merge_deploy_publish_performed", False)
        or summary.get("external_action_count", 0)
    )
    raw_private_data_inspected = bool(trace.get("raw_private_data_inspected", False))
    token_printed = bool(redaction.get("token_printed", False))
    private_kernel_exposed = bool(redaction.get("private_kernel_exposed", False))

    if missing or executed_verticals != expected_verticals:
        decision = "HOLD_MISSING_VERTICAL_RESULT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_findings:
        decision = "BLOCK_OVERCLAIM"
    elif external_action_used or raw_private_data_inspected:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif private_kernel_exposed:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif not _exists(REVIEWER_READOUT_PATH):
        decision = "HOLD_MISSING_READOUT"
    else:
        decision = "PASS_FIRST_OWNER_CONSENTED_PILOT_DRY_RUN_READY"

    result = {
        "schema": "ResidualOps_ROE13PilotDryRunGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "dry_run_id": receipt.get("dry_run_id", "") if isinstance(receipt, dict) else "",
        "vertical_count": int(summary.get("vertical_count", 0) or 0),
        "total_allow_count": int(summary.get("total_allow_count", 0) or 0),
        "total_hold_count": int(summary.get("total_hold_count", 0) or 0),
        "total_block_count": int(summary.get("total_block_count", 0) or 0),
        "missing_artifacts": missing,
        "executed_verticals": sorted(executed_verticals),
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": redaction.get("finding_count", 0),
        "claim_finding_count": len(claim_findings),
        "claim_findings": claim_findings[:50],
        "external_action_used": external_action_used,
        "raw_private_data_inspected": raw_private_data_inspected,
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
    parser = argparse.ArgumentParser(description="Run the ROE-13 pilot dry-run gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-dry-run", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe13_gate(write_result=not args.no_write, ensure_dry_run=not args.no_dry_run)
    print(
        "roe13_pilot_dry_run_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} verticals={result['vertical_count']}"
    )


if __name__ == "__main__":
    main()
