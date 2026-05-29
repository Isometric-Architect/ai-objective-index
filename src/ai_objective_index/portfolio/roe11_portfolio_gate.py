from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .residualops_portfolio_claim_audit import CLAIM_AUDIT_PATH, run_portfolio_claim_audit
from .residualops_unified_readout import (
    CLAIM_BOUNDARY_PATH,
    KNOWN_LIMITS_PATH,
    NEXT_PILOT_PLAN_PATH,
    REVIEWER_READOUT_PATH,
    UNIFIED_PORTFOLIO_PATH,
    generate_unified_portfolio,
)


OUTPUT_DIR = Path("public_launch") / "roe11"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE11_UNIFIED_PORTFOLIO_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE11_UNIFIED_PORTFOLIO_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE11_NEXT_ACTIONS.md"
MATRIX_JSON_PATH = Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.json"
MATRIX_MD_PATH = Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.md"
FEEDBACK_INDEX_PATH = Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_FEEDBACK_MEMORY_INDEX.json"
REDACTION_REPORT_PATH = Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_PORTFOLIO_REDACTION_REPORT.json"


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


def _build_summary(result: dict[str, Any]) -> str:
    return f"""# ROE-11 Unified Portfolio Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Verticals | `{result['vertical_count']}` |
| ALLOW | `{result['total_allow_count']}` |
| HOLD | `{result['total_hold_count']}` |
| BLOCK | `{result['total_block_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim audit | `{result['claim_audit_decision']}` |
| External action used | `{result['external_action_used']}` |

This is a local/offline portfolio receipt index and reviewer artifact. It is not certification, proof, product readiness, quality guarantee, or action authorization.
"""


def _build_next_actions(result: dict[str, Any]) -> str:
    next_step = "ROE-12 Owner-Consented Pilot Intake Kit" if result["decision"] == "PASS_UNIFIED_PILOT_PORTFOLIO_READY" else "resolve ROE-11 HOLD/BLOCK findings"
    return f"""# ROE-11 Next Actions

Decision: `{result['decision']}`

Recommended next step: {next_step}.

Keep the same boundaries: no external APIs, no GitHub API calls, no live MCP/tool calls, no crawling/fetching, no raw private data inspection, no token handling, no certification claim, and no external action authorization.
"""


def run_roe11_gate(write_result: bool = True, ensure_portfolio: bool = True) -> dict[str, Any]:
    generated = generate_unified_portfolio(write_result=True) if ensure_portfolio else {}
    portfolio = generated.get("portfolio") if generated else _read_json(UNIFIED_PORTFOLIO_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    claim_audit = run_portfolio_claim_audit(write_result=True)
    required = [
        UNIFIED_PORTFOLIO_PATH,
        MATRIX_JSON_PATH,
        MATRIX_MD_PATH,
        FEEDBACK_INDEX_PATH,
        REVIEWER_READOUT_PATH,
        CLAIM_BOUNDARY_PATH,
        REDACTION_REPORT_PATH,
        KNOWN_LIMITS_PATH,
        NEXT_PILOT_PLAN_PATH,
        CLAIM_AUDIT_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    vertical_summaries = portfolio.get("vertical_summaries", []) if isinstance(portfolio, dict) else []
    missing_receipts = [item.get("vertical_id", "unknown") for item in vertical_summaries if item.get("primary_decision") == "HOLD_MISSING_RECEIPT"]
    gate_failures = [item for item in vertical_summaries if not str(item.get("gate_result", "")).startswith("PASS_")]
    external_action_used = bool(portfolio.get("external_action_used", False)) if isinstance(portfolio, dict) else False
    private_kernel_exposed = bool(portfolio.get("private_kernel_exposed", False)) if isinstance(portfolio, dict) else False
    token_printed = bool(portfolio.get("token_printed", False)) if isinstance(portfolio, dict) else False

    if missing_receipts:
        decision = "HOLD_MISSING_VERTICAL_RECEIPT"
    elif missing:
        decision = "HOLD_MISSING_READOUT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_audit.get("decision") != "PASS_CLAIM_BOUNDARY_CLEAN":
        decision = "BLOCK_OVERCLAIM"
    elif external_action_used:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif private_kernel_exposed:
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSED"
    elif gate_failures:
        decision = "HOLD_MISSING_VERTICAL_RECEIPT"
    else:
        decision = "PASS_UNIFIED_PILOT_PORTFOLIO_READY"

    summary = portfolio.get("portfolio_summary", {}) if isinstance(portfolio, dict) else {}
    result = {
        "schema": "ResidualOps_ROE11UnifiedPortfolioGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "portfolio_id": portfolio.get("portfolio_id", "") if isinstance(portfolio, dict) else "",
        "vertical_count": int(summary.get("vertical_count", 0) or 0),
        "total_allow_count": int(summary.get("total_allow_count", 0) or 0),
        "total_hold_count": int(summary.get("total_hold_count", 0) or 0),
        "total_block_count": int(summary.get("total_block_count", 0) or 0),
        "missing_artifacts": missing,
        "missing_receipts": missing_receipts,
        "vertical_gate_failures": gate_failures,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "claim_audit_decision": claim_audit.get("decision", "UNKNOWN"),
        "claim_risky_phrase_count": claim_audit.get("risky_phrase_count", 0),
        "external_action_used": external_action_used,
        "live_execution_used": bool(portfolio.get("live_execution_used", False)) if isinstance(portfolio, dict) else False,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel_exposed,
        "can_certify_security": False,
        "can_prove_code_correctness": False,
        "can_prove_legal_privacy_license_eval_status": False,
        "can_guarantee_quality": False,
        "can_claim_product_readiness": False,
        "can_authorize_external_action": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, _build_summary(result))
        _write_text(NEXT_ACTIONS_PATH, _build_next_actions(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-11 unified pilot portfolio gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-generate", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe11_gate(write_result=not args.no_write, ensure_portfolio=not args.no_generate)
    print(
        "roe11_portfolio_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} claim_audit={result['claim_audit_decision']}"
    )


if __name__ == "__main__":
    main()
