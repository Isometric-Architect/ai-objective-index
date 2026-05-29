from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .residualops_feedback_memory_index import build_feedback_memory_index, write_feedback_memory_index
from .residualops_portfolio_loader import load_all_pilot_receipts
from .residualops_portfolio_redaction import scan_portfolio_artifacts
from .residualops_vertical_matrix import build_vertical_matrix, matrix_to_markdown, write_vertical_matrix


PORTFOLIO_DIR = Path("pilot_receipts") / "portfolio"
UNIFIED_PORTFOLIO_PATH = PORTFOLIO_DIR / "RESIDUALOPS_UNIFIED_PILOT_PORTFOLIO.json"
REVIEWER_READOUT_PATH = PORTFOLIO_DIR / "RESIDUALOPS_PORTFOLIO_REVIEWER_READOUT.md"
CLAIM_BOUNDARY_PATH = PORTFOLIO_DIR / "RESIDUALOPS_PORTFOLIO_CLAIM_BOUNDARY.md"
KNOWN_LIMITS_PATH = PORTFOLIO_DIR / "RESIDUALOPS_PORTFOLIO_KNOWN_LIMITS.md"
NEXT_PILOT_PLAN_PATH = PORTFOLIO_DIR / "RESIDUALOPS_NEXT_PILOT_PLAN.md"


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


def _vertical_summary(vertical: dict[str, Any]) -> dict[str, Any]:
    return {
        "vertical_id": vertical["vertical_id"],
        "name": vertical["name"],
        "scope": vertical["scope"],
        "receipt_path": vertical["receipt_path"],
        "gate_result": vertical["gate_result"],
        "allow_count": vertical["allow_count"],
        "hold_count": vertical["hold_count"],
        "block_count": vertical["block_count"],
        "primary_decision": vertical["primary_decision"],
        "no_external_action": vertical["no_external_action"],
        "redaction_status": vertical["redaction_status"],
        "feedback_memory_status": vertical["feedback_memory_status"],
        "key_next_actions": vertical["key_next_actions"],
    }


def _collect_reasons(loaded: dict[str, Any], key: str) -> list[str]:
    reasons: list[str] = []
    for vertical in loaded["verticals"]:
        reasons.extend(vertical.get(key, []))
    return reasons[:10]


def build_unified_portfolio(loaded: dict[str, Any] | None = None) -> dict[str, Any]:
    loaded = loaded or load_all_pilot_receipts()
    vertical_summaries = [_vertical_summary(vertical) for vertical in loaded["verticals"]]
    total_allow = sum(item["allow_count"] for item in vertical_summaries)
    total_hold = sum(item["hold_count"] for item in vertical_summaries)
    total_block = sum(item["block_count"] for item in vertical_summaries)
    return {
        "schema": "ResidualOps_UnifiedPilotPortfolio/v0.1",
        "generated_at": _timestamp(),
        "portfolio_id": "residualops-unified-pilot-portfolio-v0-1",
        "verticals": ["agentsec", "qira", "datacapsule"],
        "portfolio_summary": {
            "vertical_count": len(vertical_summaries),
            "total_allow_count": total_allow,
            "total_hold_count": total_hold,
            "total_block_count": total_block,
            "top_hold_reasons": _collect_reasons(loaded, "top_hold_reasons"),
            "top_block_reasons": _collect_reasons(loaded, "top_block_reasons"),
            "common_claim_boundaries": [
                "not security certification",
                "not code correctness proof",
                "not legal/privacy/license/evaluation proof",
                "not quality guarantee",
                "not product ready",
                "no external action authorization",
            ],
        },
        "shared_kernel": {
            "packet": True,
            "check_or_probe": True,
            "receipt": True,
            "allow_hold_block": True,
            "feedback_memory": True,
        },
        "vertical_summaries": vertical_summaries,
        "portfolio_claim_boundary": {
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
        "known_limits": [
            "local/offline pilot receipt index only",
            "no external APIs or GitHub APIs",
            "no live MCP/tool calls",
            "no crawling, URL fetching, raw private data inspection, upload, or model training",
            "not certification, proof, legal opinion, privacy audit, license clearance, quality guarantee, product-readiness claim, or action authorization",
            "private weights, thresholds, provider priors, anti-gaming logic, private negative controls, private probe seeds, and commercial routing policy remain non-public",
        ],
        "recommended_next_package": "ROE-12 Owner-Consented Pilot Intake Kit",
        "external_action_used": loaded["external_action_used"],
        "live_execution_used": loaded["live_execution_used"],
        "token_printed": False,
        "private_kernel_exposed": False,
    }


def build_reviewer_readout(portfolio: dict[str, Any], matrix: dict[str, Any], feedback_index: dict[str, Any]) -> str:
    summary = portfolio["portfolio_summary"]
    lines = [
        "# ResidualOps Unified Pilot Portfolio Readout",
        "",
        "ResidualOps is presented here as a local/offline receipt portfolio pattern: Packet -> Check/Probe -> Receipt -> ALLOW/HOLD/BLOCK -> Feedback Memory.",
        "",
        "## Verticals",
        "",
        "| Vertical | Scope | Gate | ALLOW | HOLD | BLOCK | Primary decision |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for vertical in portfolio["vertical_summaries"]:
        lines.append(
            f"| {vertical['name']} | {vertical['scope']} | `{vertical['gate_result']}` | `{vertical['allow_count']}` | `{vertical['hold_count']}` | `{vertical['block_count']}` | `{vertical['primary_decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary Counts",
            "",
            f"- Verticals: `{summary['vertical_count']}`",
            f"- ALLOW: `{summary['total_allow_count']}`",
            f"- HOLD: `{summary['total_hold_count']}`",
            f"- BLOCK: `{summary['total_block_count']}`",
            "",
            "## Matrix",
            "",
            matrix_to_markdown(matrix),
            "## Feedback Memory",
            "",
            f"- Entries indexed: `{feedback_index['entry_count']}`",
            "- Portfolio next actions: owner-consented pilot intake, second-run receipt, unified dashboard, pilot feedback form, private kernel protection.",
            "",
            "## What This Is Not",
            "",
            "- Not security certification.",
            "- Not code correctness proof.",
            "- Not legal, privacy, license, or evaluation-cleanliness proof.",
            "- Not a quality guarantee.",
            "- Not product readiness.",
            "- No external action authorization.",
            "",
            "## Next Actions",
            "",
            "- ROE-12 Owner-Consented Pilot Intake Kit.",
            "- Optional AOI 0.3.0a2 MCP Registry recovery backlog.",
            "- Keep private kernels private.",
            "",
        ]
    )
    return "\n".join(lines)


def build_claim_boundary_markdown() -> str:
    return """# ResidualOps Portfolio Claim Boundary

This portfolio readout is a local/offline receipt index and reviewer artifact.

It is not:

- no security certification
- no code correctness proof
- no legal opinion
- no privacy audit
- no license clearance
- no evaluation-cleanliness proof
- no quality guarantee
- no product-readiness claim
- no merge, deploy, training, purchase, or external action authorization

It may say:

- local/offline receipt
- reviewer artifact
- ALLOW/HOLD/BLOCK finding
- known limit
- feedback memory
- claim boundary
- no external action
"""


def build_known_limits_markdown() -> str:
    return """# ResidualOps Portfolio Known Limits

- Reads only existing local pilot receipt artifacts.
- Does not call external APIs, GitHub APIs, live MCP servers, or external tools.
- Does not crawl, fetch URLs, inspect raw private data, upload data, train models, deploy, publish, merge, or post comments.
- Does not expose private weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, or commercial routing policy.
- Does not certify security, prove code correctness, prove legal/privacy/license/evaluation-cleanliness status, guarantee quality, claim product readiness, or authorize actions.
"""


def build_next_plan_markdown() -> str:
    return """# ResidualOps Next Pilot Plan

Recommended next package: ROE-12 Owner-Consented Pilot Intake Kit.

ROE-12 should collect local manifests or patch/corpus packets only when the owner has explicitly provided consent. It should preserve the same no-network, no-live-execution, no-token, no-certification, and no-action-authorization boundaries.

Secondary backlog: AOI 0.3.0a2 MCP Registry recovery, if Registry namespace/version recovery remains useful.
"""


def generate_unified_portfolio(write_result: bool = True) -> dict[str, Any]:
    loaded = load_all_pilot_receipts()
    portfolio = build_unified_portfolio(loaded)
    matrix = write_vertical_matrix(loaded) if write_result else build_vertical_matrix(loaded)
    feedback_index = write_feedback_memory_index(loaded) if write_result else build_feedback_memory_index(loaded)
    artifacts_to_scan = [
        UNIFIED_PORTFOLIO_PATH,
        Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.json",
        Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.md",
        Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_FEEDBACK_MEMORY_INDEX.json",
        REVIEWER_READOUT_PATH,
        CLAIM_BOUNDARY_PATH,
        KNOWN_LIMITS_PATH,
        NEXT_PILOT_PLAN_PATH,
    ]
    if write_result:
        _write_json(UNIFIED_PORTFOLIO_PATH, portfolio)
        _write_text(REVIEWER_READOUT_PATH, build_reviewer_readout(portfolio, matrix, feedback_index))
        _write_text(CLAIM_BOUNDARY_PATH, build_claim_boundary_markdown())
        _write_text(KNOWN_LIMITS_PATH, build_known_limits_markdown())
        _write_text(NEXT_PILOT_PLAN_PATH, build_next_plan_markdown())
        redaction = scan_portfolio_artifacts(artifacts_to_scan)
    else:
        redaction = {"decision": "NOT_WRITTEN"}
    return {
        "portfolio": portfolio,
        "matrix": matrix,
        "feedback_memory_index": feedback_index,
        "redaction": redaction,
        "paths": {
            "portfolio": str(UNIFIED_PORTFOLIO_PATH).replace("\\", "/"),
            "reviewer_readout": str(REVIEWER_READOUT_PATH).replace("\\", "/"),
            "claim_boundary": str(CLAIM_BOUNDARY_PATH).replace("\\", "/"),
            "known_limits": str(KNOWN_LIMITS_PATH).replace("\\", "/"),
            "next_pilot_plan": str(NEXT_PILOT_PLAN_PATH).replace("\\", "/"),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the ROE-11 unified ResidualOps pilot portfolio readout.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing artifacts.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = generate_unified_portfolio(write_result=not args.no_write)
    summary = result["portfolio"]["portfolio_summary"]
    print(
        "residualops_unified_readout: "
        f"verticals={summary['vertical_count']} allow={summary['total_allow_count']} "
        f"hold={summary['total_hold_count']} block={summary['total_block_count']} "
        f"redaction={result['redaction']['decision']}"
    )


if __name__ == "__main__":
    main()
