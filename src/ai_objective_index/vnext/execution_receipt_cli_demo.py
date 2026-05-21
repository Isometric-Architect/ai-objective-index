from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.integrated_store import get_store_for_scope

from .execution_receipt_loop import ExecutionReceiptSubmission
from .execution_receipt_store import (
    ExecutionReceiptStore,
    SAMPLE_RECEIPT_INDEX_PATH,
    SAMPLE_RECEIPT_STORE_PATH,
)
from .execution_receipt_validation import validate_execution_receipt
from .objective_router_models import ObjectiveRouteRequest
from .receipt_router_adapter import route_objective_with_receipts


WAVE6_DIR = Path("public_launch") / "wave6"
SAMPLE_SUBMISSION_PATH = WAVE6_DIR / "EXECUTION_RECEIPT_SAMPLE_SUBMISSION.json"
VALIDATION_RESULT_PATH = WAVE6_DIR / "EXECUTION_RECEIPT_VALIDATION_RESULT.json"
MEMORY_SAMPLE_PATH = WAVE6_DIR / "CAPABILITY_RECEIPT_MEMORY_SAMPLE.json"
OBJECTIVE_SUMMARY_SAMPLE_PATH = WAVE6_DIR / "OBJECTIVE_RECEIPT_SUMMARY_SAMPLE.json"
ROUTE_OVERLAY_SAMPLE_PATH = WAVE6_DIR / "RECEIPT_ROUTE_OVERLAY_SAMPLE.json"
RESULT_PATH = WAVE6_DIR / "PACKAGE_9D_EXECUTION_RECEIPT_LOOP_RESULT.json"
NEXT_STEPS_PATH = WAVE6_DIR / "PACKAGE_9D_NEXT_STEPS.md"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _sample_candidate(data_scope: str) -> tuple[str, str]:
    try:
        store = get_store_for_scope(data_scope)
        objects = store.search_objects("browser automation MCP server", domain="mcp_servers", limit=1)
        if not objects:
            objects = store.list_objects()[:1]
        if objects:
            obj = objects[0]
            return f"capability:{obj.object_id}", obj.name
    except Exception:
        pass
    return "capability:aoi-pixelforge-api", "AOI sample capability"


def run_execution_receipt_cli_demo(data_scope: str = "public_beta_mcp") -> dict[str, Any]:
    capability_id, capability_name = _sample_candidate(data_scope)
    submission = ExecutionReceiptSubmission(
        objective_id="objective-browser-automation-mcp",
        capability_id=capability_id,
        object_id=capability_id.removeprefix("capability:"),
        capability_name=capability_name,
        data_scope=data_scope,
        submitted_by="local_test",
        receipt_origin="local_fixture",
        outcome="hold",
        outcome_summary="Local fixture found policy clarity still insufficient for stronger route use.",
        task_context="Offline receipt-loop demo for browser automation MCP candidate routing.",
        environment_class="local",
        constraints_checked=["require_source_trace", "require_policy_clarity"],
        observed_outputs=["Route remained conservative and did not execute external tools."],
        error_type="policy_unclear",
        residual_found=True,
        residual_notes=["Policy/privacy/data-retention fields require manual review before stronger use."],
        missing_fields_found=["privacy_policy", "data_retention_policy", "pricing"],
        route_decision_before="HOLD_POLICY_CLARITY",
        route_decision_after="HOLD_POLICY_CLARITY",
    )
    validation = validate_execution_receipt(submission)
    store = ExecutionReceiptStore(SAMPLE_RECEIPT_STORE_PATH, SAMPLE_RECEIPT_INDEX_PATH)
    store.receipt_path.parent.mkdir(parents=True, exist_ok=True)
    store.receipt_path.write_text("", encoding="utf-8")
    store.index_path.write_text(
        json.dumps(
            {"schema": "AOI_ExecutionReceiptIndex/v0.1", "receipt_count": 0, "receipts": [], "token_printed": False},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    stored = store.append_receipt(submission, validation)
    memory = store.summarize_by_capability(capability_id)
    objective_summary = store.summarize_by_objective("objective-browser-automation-mcp")
    request = ObjectiveRouteRequest(
        query="browser automation MCP server",
        objective="select source-traced MCP candidates",
        data_scope=data_scope,  # type: ignore[arg-type]
        limit=5,
        constraints={"require_policy_clarity": True},
    )
    route_with_receipts = route_objective_with_receipts(request, store=store)
    overlay = route_with_receipts.get("receipt_route_overlay", {})
    result = {
        "schema": "AOI_Package9DExecutionReceiptLoopResult/v0.1",
        "receipt_id": submission.receipt_id,
        "validation_decision": validation.decision,
        "stored_sample_fixture": True,
        "sample_store_path": str(SAMPLE_RECEIPT_STORE_PATH),
        "capability_id": capability_id,
        "memory_status": memory["memory_status"],
        "receipt_memory_applied": overlay.get("receipt_memory_applied", False),
        "external_execution": False,
        "probe_execution": False,
        "gateway_execution": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    _write_json(SAMPLE_SUBMISSION_PATH, submission.model_dump(mode="json", by_alias=True))
    _write_json(VALIDATION_RESULT_PATH, validation.model_dump(mode="json", by_alias=True))
    _write_json(MEMORY_SAMPLE_PATH, memory)
    _write_json(OBJECTIVE_SUMMARY_SAMPLE_PATH, objective_summary)
    _write_json(ROUTE_OVERLAY_SAMPLE_PATH, route_with_receipts)
    _write_json(RESULT_PATH, result)
    NEXT_STEPS_PATH.write_text(
        "# Package 9D Next Steps\n\n"
        "- Use receipt memory to record manual outcomes and known failures.\n"
        "- Keep receipts local/offline unless a later package defines a publication policy.\n"
        "- Receipts can warn or downgrade routes, but they cannot verify, certify, guarantee quality, or authorize actions.\n"
        "- Recommended next package: Package 9E Probe-before-Use MVP.\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the offline Package 9D execution receipt loop demo.")
    parser.add_argument("--data-scope", default="public_beta_mcp")
    args = parser.parse_args()
    result = run_execution_receipt_cli_demo(data_scope=args.data_scope)
    print(
        "execution_receipt_cli_demo: "
        f"validation={result['validation_decision']} memory_status={result['memory_status']} "
        "external_execution=False probe_execution=False"
    )


if __name__ == "__main__":
    main()
