from __future__ import annotations

import argparse
import json
from pathlib import Path

from .trust_report import build_capability_trust_report


REPORT_PATH = Path("public_launch") / "wave4" / "CAPABILITY_TRUST_SAMPLE_REPORT.json"
RESULT_PATH = Path("public_launch") / "wave4" / "PACKAGE_9B_CAPABILITY_TRUST_RESULT.json"
NEXT_STEPS_PATH = Path("public_launch") / "wave4" / "PACKAGE_9B_NEXT_STEPS.md"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_next_steps() -> None:
    NEXT_STEPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    NEXT_STEPS_PATH.write_text(
        """# Package 9B Next Steps

Recommended next package: Package 9C Objective Router API MVP.

Package 9B created a local/offline capability trust schema MVP. It did not run probes, execute a gateway, upload to PyPI, submit to MCP Registry, or post to communities.

Next, Package 9C can expose these trust cards through a read-only Objective Router API while preserving ALLOW/HOLD/BLOCK claim boundaries.
""",
        encoding="utf-8",
    )


def run_trust_cli(
    query: str,
    objective: str,
    data_scope: str = "sample",
    domain: str = "mixed_ai_tools",
    limit: int = 10,
) -> dict:
    report = build_capability_trust_report(
        query=query,
        objective=objective,
        domain=domain,
        data_scope=data_scope,
        limit=limit,
    )
    _write_json(REPORT_PATH, report)
    result = {
        "overall_token": "PASS",
        "report_path": str(REPORT_PATH),
        "candidate_count": report["summary"]["candidate_count"],
        "route_decision_counts": report["summary"]["route_decision_counts"],
        "offline_only": True,
        "network_used": False,
        "probe_execution_performed": False,
        "gateway_execution_performed": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
    }
    _write_json(RESULT_PATH, result)
    _write_next_steps()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an offline AOI vNext capability trust report.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--data-scope", default="sample")
    parser.add_argument("--domain", default="mixed_ai_tools")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    report = run_trust_cli(
        query=args.query,
        objective=args.objective,
        data_scope=args.data_scope,
        domain=args.domain,
        limit=args.limit,
    )
    print("AOI vNext capability trust report")
    print(f"data_scope={report['data_scope']} candidates={report['summary']['candidate_count']}")
    print("decision counts:", json.dumps(report["summary"]["route_decision_counts"], sort_keys=True))
    for card in report["trust_cards"][: args.limit]:
        print(
            f"- {card['name']}: {card['route_decision']['decision']} "
            f"score={card['score_components']['capability_trust']['demo_trust_score']}"
        )


if __name__ == "__main__":
    main()
