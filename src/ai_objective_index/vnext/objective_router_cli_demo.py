from __future__ import annotations

import argparse
import json
from pathlib import Path

from .objective_router import route_objective
from .objective_router_models import ObjectiveRouteRequest


OUTPUT_PATH = Path("public_launch") / "wave5" / "OBJECTIVE_ROUTER_SAMPLE_RESPONSE.json"
RESULT_PATH = Path("public_launch") / "wave5" / "PACKAGE_9C_OBJECTIVE_ROUTER_RESULT.json"
NEXT_STEPS_PATH = Path("public_launch") / "wave5" / "PACKAGE_9C_NEXT_STEPS.md"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_demo(
    query: str,
    objective: str,
    data_scope: str = "sample",
    domain: str = "mcp_servers",
    limit: int = 10,
) -> dict:
    response = route_objective(
        ObjectiveRouteRequest(
            query=query,
            objective=objective,
            data_scope=data_scope,  # type: ignore[arg-type]
            domain=domain,
            limit=limit,
        )
    )
    payload = response.model_dump(mode="json", by_alias=True)
    _write_json(OUTPUT_PATH, payload)
    result = {
        "overall_token": "PASS",
        "sample_response_path": str(OUTPUT_PATH),
        "total_candidates": payload["route_summary"]["total_candidates"],
        "allow_count": payload["route_summary"]["allow_count"],
        "hold_count": payload["route_summary"]["hold_count"],
        "block_count": payload["route_summary"]["block_count"],
        "offline_only": True,
        "network_used": False,
        "probe_execution_performed": False,
        "gateway_execution_performed": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
    }
    _write_json(RESULT_PATH, result)
    NEXT_STEPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    NEXT_STEPS_PATH.write_text(
        """# Package 9C Next Steps

Recommended next package: Package 9D ExecutionReceipt Loop MVP.

Package 9C exposes Objective Router route decisions through read-only REST/MCP surfaces. Package 9D can add an offline ExecutionReceipt loop for capturing route outcomes without running live probes or gateway actions.
""",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an offline Objective Router demo.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--data-scope", default="sample")
    parser.add_argument("--domain", default="mcp_servers")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    payload = run_demo(
        query=args.query,
        objective=args.objective,
        data_scope=args.data_scope,
        domain=args.domain,
        limit=args.limit,
    )
    print("AOI vNext Objective Router")
    print(f"data_scope={payload['data_scope']} candidates={payload['route_summary']['total_candidates']}")
    print(
        "counts="
        + json.dumps(
            {
                "allow": payload["route_summary"]["allow_count"],
                "hold": payload["route_summary"]["hold_count"],
                "block": payload["route_summary"]["block_count"],
            },
            sort_keys=True,
        )
    )
    for card in payload["results"][: args.limit]:
        print(f"- {card['name']}: {card['route_decision']['decision']} - {card['route_decision']['reason']}")


if __name__ == "__main__":
    main()
