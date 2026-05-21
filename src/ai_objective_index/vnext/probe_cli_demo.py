from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .objective_router import route_objective
from .objective_router_models import ObjectiveRouteRequest
from .probe_negative_controls import run_negative_controls
from .probe_receipt_store import (
    ProbeReceiptStore,
    SAMPLE_PROBE_RECEIPT_INDEX_PATH,
    SAMPLE_PROBE_RECEIPT_STORE_PATH,
)
from .probe_route_adapter import build_probe_plan_for_route, overlay_probe_results
from .probe_runner import run_probe_plan


WAVE7_DIR = Path("public_launch") / "wave7"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _reset_sample_store() -> ProbeReceiptStore:
    for path in [SAMPLE_PROBE_RECEIPT_STORE_PATH, SAMPLE_PROBE_RECEIPT_INDEX_PATH]:
        full = Path.cwd() / path
        if full.exists():
            full.unlink()
    return ProbeReceiptStore(SAMPLE_PROBE_RECEIPT_STORE_PATH, SAMPLE_PROBE_RECEIPT_INDEX_PATH)


def run_probe_cli_demo(
    query: str,
    objective: str,
    data_scope: str = "public_beta_mcp",
    limit: int = 5,
) -> dict[str, Any]:
    request = ObjectiveRouteRequest(query=query, objective=objective, data_scope=data_scope, limit=limit)  # type: ignore[arg-type]
    route_payload = route_objective(request).model_dump(mode="json", by_alias=True)
    plan = build_probe_plan_for_route(route_payload, route_request=request.model_dump(mode="json"))
    receipt = run_probe_plan(plan)
    negative_controls = run_negative_controls()
    store = _reset_sample_store()
    stored = store.append_probe_receipt(receipt)
    first_capability = plan.capability_ids[0] if plan.capability_ids else "capability:not-found"
    memory = store.build_capability_probe_memory(first_capability)
    overlay = overlay_probe_results(route_payload, receipt, route_request=request.model_dump(mode="json"))

    plan_payload = plan.model_dump(mode="json", by_alias=True)
    receipt_payload = receipt.model_dump(mode="json", by_alias=True)
    memory_payload = memory.model_dump(mode="json", by_alias=True)
    overlay_payload = overlay.model_dump(mode="json", by_alias=True)
    route_result_counts = receipt.aggregate.model_dump(mode="json")

    _write_json(WAVE7_DIR / "PROBE_PLAN_SAMPLE.json", plan_payload)
    _write_json(WAVE7_DIR / "PROBE_RUN_SAMPLE_RESULT.json", receipt_payload)
    _write_json(WAVE7_DIR / "PROBE_NEGATIVE_CONTROL_RESULT.json", negative_controls)
    _write_json(WAVE7_DIR / "CAPABILITY_PROBE_MEMORY_SAMPLE.json", memory_payload)
    _write_json(WAVE7_DIR / "PROBE_ROUTE_OVERLAY_SAMPLE.json", overlay_payload)

    result = {
        "schema": "AOI_Package9EProbeBeforeUseResult/v0.1",
        "package": "9E",
        "query": query,
        "objective": objective,
        "data_scope": data_scope,
        "candidate_count": route_payload.get("route_summary", {}).get("total_candidates", 0),
        "probe_plan_id": plan.plan_id,
        "probe_card_count": len(plan.probe_cards),
        "probe_receipt_id": receipt.receipt_id,
        "probe_result_counts": route_result_counts,
        "negative_control_token": negative_controls["overall_token"],
        "negative_control_false_pass_count": negative_controls["false_pass_count"],
        "capability_probe_memory_status": memory.memory_status,
        "probe_route_overlay_applied": overlay.probe_memory_applied,
        "stored_sample_receipt_id": stored["receipt"]["receipt_id"],
        "network_used": False,
        "external_tool_execution": False,
        "gateway_execution": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
        "claim_boundary": "local probe pass is not verification, not security certification, not quality guarantee, and not action authorization",
    }
    _write_json(WAVE7_DIR / "PACKAGE_9E_PROBE_BEFORE_USE_RESULT.json", result)
    next_steps = """# Package 9E Next Steps

Recommended next step: resume the local PyPI build path only after confirming the vNext probe wording remains conservative, or continue to Package 9F vNext distribution gate.

Package 9E did not upload to PyPI/TestPyPI, submit to MCP Registry, post to communities, run live probes, call live MCP servers, fetch URLs, execute external tools, or authorize actions.
"""
    (WAVE7_DIR / "PACKAGE_9E_NEXT_STEPS.md").write_text(next_steps, encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local-only vNext probe-before-use demo.")
    parser.add_argument("--query", default="browser automation MCP server")
    parser.add_argument("--objective", default="select source-traced MCP candidates")
    parser.add_argument("--data-scope", default="public_beta_mcp")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    result = run_probe_cli_demo(
        query=args.query,
        objective=args.objective,
        data_scope=args.data_scope,
        limit=args.limit,
    )
    print(
        "probe_cli_demo: "
        f"candidates={result['candidate_count']} probe_cards={result['probe_card_count']} "
        f"negative_controls={result['negative_control_token']}"
    )


if __name__ == "__main__":
    main()
