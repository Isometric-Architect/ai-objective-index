from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_DIR = Path("public_launch") / "roe0"
OUTPUT_PATH = OUTPUT_DIR / "ROE_PORTFOLIO_STRATEGY.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE0_SUMMARY.md"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_portfolio_strategy() -> dict[str, Any]:
    implementation_sequence = [
        {
            "order": 0,
            "package": "ROE-0",
            "track": "portfolio_strategy_and_protection",
            "product": "ResidualOps Portfolio Kernel",
            "decision": "IMPLEMENT_NOW",
            "reason": "Lock the public/private split, product order, and QBCPL coding governance before opening more surface area.",
        },
        {
            "order": 1,
            "package": "QIRA-1",
            "track": "first_implementation_vertical",
            "product": "QIRA-Code ReleaseGate",
            "decision": "BUILD_FIRST",
            "reason": "QBCPL RUN019 is the most concrete local source: behavior contracts, patch receipts, residual ledgers, and action-license boundaries map directly to a GitHub Action/CLI MVP.",
        },
        {
            "order": 2,
            "package": "AgentSec-1",
            "track": "first_market_security_vertical",
            "product": "AgentSec Gate",
            "decision": "BUILD_SECOND",
            "reason": "Agent/MCP/tool-call security has the strongest market signal, but it should reuse the QIRA receipt, residual, and license primitives instead of starting as a separate stack.",
        },
        {
            "order": 3,
            "package": "DataCapsule-1",
            "track": "data_governance_vertical",
            "product": "DataCapsule / AIDREG Engine",
            "decision": "BUILD_THIRD",
            "reason": "Data rights, source, poison, eval-leak, and use-permission routing are large-platform candidates; the first version should reuse the same packet/probe/receipt pattern after QIRA and AgentSec stabilize it.",
        },
    ]
    market_priority = [
        {"rank": 1, "product": "AgentSec Gate", "why": "largest immediate security and MCP/tool-call buyer signal"},
        {"rank": 2, "product": "DataCapsule / AIDREG Engine", "why": "large AI data governance platform potential"},
        {"rank": 3, "product": "QIRA-Code ReleaseGate", "why": "fastest MVP and proof loop through GitHub/CI workflows"},
    ]
    common_kernel = {
        "public_kernel_language": [
            "Packet",
            "Probe",
            "Validator",
            "ResidualLedger",
            "Receipt",
            "CertCost",
            "d_raw/d_eco",
            "ALLOW/HOLD/BLOCK",
        ],
        "private_kernel_reserved": [
            "ranking-weight values",
            "threshold policy",
            "anti-gaming rules",
            "provider trust priors",
            "private negative-control bank",
            "private probe seeds",
            "commercial routing policy",
            "enterprise data policy",
        ],
    }
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": "PASS_PORTFOLIO_SEQUENCE_LOCKED",
        "strategy": "Build a shared ResidualOps operating kernel and productize it through narrow verticals rather than launching three broad products at once.",
        "implementation_sequence": implementation_sequence,
        "market_priority": market_priority,
        "selected_next_package": "QIRA-1",
        "selected_next_package_name": "QIRA-Code ReleaseGate MVP",
        "rationale": [
            "QIRA is first for implementation because QBCPL provides concrete local coding objects and validators.",
            "AgentSec remains the first external market/security story and should follow with reused route and receipt primitives.",
            "DataCapsule is the long-platform track and should follow once the packet/receipt loop is proven.",
        ],
        "common_kernel": common_kernel,
        "public_claim_ceiling": [
            "strategy and schema alignment",
            "local/offline prototype planning",
            "source-traced route decisions",
            "receipt and residual memory language",
        ],
        "must_not_claim": [
            "verified",
            "safe",
            "security certified",
            "quality guaranteed",
            "product ready",
            "legal/financial/medical advice",
            "purchasing advice",
            "external action authorization",
        ],
        "external_actions_performed": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }


def build_summary_markdown(result: dict[str, Any]) -> str:
    sequence_rows = "\n".join(
        f"| {item['order']} | {item['package']} | {item['product']} | {item['decision']} |"
        for item in result["implementation_sequence"]
    )
    market_rows = "\n".join(
        f"| {item['rank']} | {item['product']} | {item['why']} |"
        for item in result["market_priority"]
    )
    return f"""# ROE-0 Portfolio Strategy Summary

Decision: `{result['decision']}`

ROE-0 keeps AOI as the live public router while preparing a parallel ResidualOps product family. The first move is not to build three broad products at once. The safer sequence is to lock the shared kernel and then ship narrow verticals that reuse the same packet, residual, receipt, and ALLOW/HOLD/BLOCK discipline.

## Implementation Sequence

| Order | Package | Product | Decision |
| --- | --- | --- | --- |
{sequence_rows}

## Market Priority

| Rank | Product | Reason |
| --- | --- | --- |
{market_rows}

## Claim Boundary

ROE-0 is strategy, schema, and productization planning. It is not verification, security certification, a quality guarantee, product readiness, legal advice, purchasing advice, or external action authorization.
"""


def run_portfolio_strategy(write_result: bool = True) -> dict[str, Any]:
    result = build_portfolio_strategy()
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write_text(SUMMARY_PATH, build_summary_markdown(result))
    return result


def main() -> None:
    result = run_portfolio_strategy()
    print(f"roe_portfolio_strategy: {result['decision']} next={result['selected_next_package']}")


if __name__ == "__main__":
    main()
