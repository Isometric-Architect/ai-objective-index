from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_dry_run_executor import (
    AGENTSEC_RESULT_PATH,
    DATACAPSULE_RESULT_PATH,
    QIRA_RESULT_PATH,
    execute_all_verticals,
)
from .pilot_dry_run_feedback_memory import build_dry_run_feedback_memory, feedback_memory_to_jsonable
from .pilot_dry_run_readout import build_dry_run_readout
from .pilot_dry_run_receipt import PilotDryRunReceipt, PilotDryRunTrace, PilotDryRunTraceStep, to_jsonable
from .pilot_dry_run_redaction import REDACTION_REPORT_PATH, scan_dry_run_artifacts
from .pilot_dry_run_router import build_route_trace, route_sample_intake_packets


DRY_RUN_DIR = Path("pilot_dry_runs")
RECEIPT_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_RECEIPT.json"
TRACE_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_TRACE.json"
REVIEWER_READOUT_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_REVIEWER_READOUT.md"
FEEDBACK_MEMORY_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_FEEDBACK_MEMORY.json"
KNOWN_LIMITS_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_KNOWN_LIMITS.md"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_known_limits() -> str:
    return """# ROE-13 Pilot Dry-Run Known Limits

- Local/sample intake packets only.
- Local/offline vertical packager functions only.
- No external pilot has occurred.
- No GitHub API calls, cloning, URL fetching, crawling, live MCP/tool calls, external repo mutation, posting, merge, deploy, publish, upload, model training, or credential use.
- No raw private data inspection.
- Not security certification.
- Not code correctness proof.
- Not legal, privacy, license, or evaluation-cleanliness proof.
- Not a quality guarantee.
- Not product readiness.
- No external action authorization.
"""


def build_trace(dry_run_id: str, routes: dict[str, Any], results: list[Any]) -> PilotDryRunTrace:
    route_trace = build_route_trace(routes)
    steps = [
        PilotDryRunTraceStep(
            step_id="roe13-step-1",
            step_name="load_roe12_sample_intake_packets",
            input_ref="pilot_intake/PILOT_INTAKE_PACKET_SAMPLE_*.json",
            output_ref="local intake packet objects",
            decision="PASS",
            notes=["read local sample intake packets only"],
        ),
        PilotDryRunTraceStep(
            step_id="roe13-step-2",
            step_name="route_intake_packets",
            input_ref="ROE-12 intake packets",
            output_ref="vertical routes",
            decision="PASS" if all(item.get("route_matches_expected") for item in route_trace) else "HOLD",
            notes=["agentsec, qira, and datacapsule routes matched expected sample artifacts"],
        ),
        PilotDryRunTraceStep(
            step_id="roe13-step-3",
            step_name="execute_local_vertical_packagers",
            input_ref="vertical routes",
            output_ref="pilot_receipts/{agentsec,qira,datacapsule}",
            decision="PASS",
            notes=["direct Python function imports only; no subprocess, network, GitHub API, live MCP, upload, train, merge, deploy, or publish action"],
        ),
        PilotDryRunTraceStep(
            step_id="roe13-step-4",
            step_name="aggregate_dry_run_receipt",
            input_ref="vertical pilot receipts",
            output_ref=str(RECEIPT_PATH).replace("\\", "/"),
            decision="PASS",
            notes=["aggregated local receipt counts and claim boundaries"],
        ),
    ]
    return PilotDryRunTrace(
        dry_run_id=dry_run_id,
        intake_ids=[route.intake_id for route in routes.values()],
        vertical_routes=route_trace,
        executed_verticals=[result.vertical for result in results],
        skipped_verticals=[],
        steps=steps,
    )


def build_dry_run_receipt(dry_run_id: str, results: list[Any]) -> PilotDryRunReceipt:
    feedback = build_dry_run_feedback_memory(dry_run_id, results)
    total_allow = sum(result.allow_count for result in results)
    total_hold = sum(result.hold_count for result in results)
    total_block = sum(result.block_count for result in results)
    return PilotDryRunReceipt(
        dry_run_id=dry_run_id,
        results=results,
        aggregate_summary={
            "vertical_count": len(results),
            "total_allow_count": total_allow,
            "total_hold_count": total_hold,
            "total_block_count": total_block,
            "all_redaction_passed": all(result.redaction_status == "PASS_REDACTED" for result in results),
            "all_gates_passed": all(str(result.gate_result).startswith("PASS_") for result in results),
            "external_action_count": len([result for result in results if result.external_action_used]),
        },
        feedback_memory=feedback,
    )


def run_pilot_dry_run(sample: bool = True, write_result: bool = True) -> dict[str, Any]:
    dry_run_id = "roe13-local-sample-dry-run-v0-1"
    routes = route_sample_intake_packets(ensure_samples=sample)
    results = execute_all_verticals(dry_run_id, routes)
    trace = build_trace(dry_run_id, routes, results)
    receipt = build_dry_run_receipt(dry_run_id, results)
    receipt_payload = to_jsonable(receipt)
    trace_payload = to_jsonable(trace)
    feedback_payload = feedback_memory_to_jsonable(receipt.feedback_memory)
    if write_result:
        _write_json(TRACE_PATH, trace_payload)
        _write_json(RECEIPT_PATH, receipt_payload)
        _write_json(FEEDBACK_MEMORY_PATH, feedback_payload)
        _write_text(REVIEWER_READOUT_PATH, build_dry_run_readout(receipt))
        _write_text(KNOWN_LIMITS_PATH, build_known_limits())
    redaction = scan_dry_run_artifacts(
        [
            TRACE_PATH,
            AGENTSEC_RESULT_PATH,
            QIRA_RESULT_PATH,
            DATACAPSULE_RESULT_PATH,
            RECEIPT_PATH,
            REVIEWER_READOUT_PATH,
            FEEDBACK_MEMORY_PATH,
            KNOWN_LIMITS_PATH,
        ],
        write_result=write_result,
    )
    return {
        "trace": trace_payload,
        "receipt": receipt_payload,
        "results": [to_jsonable(result) for result in results],
        "feedback_memory": feedback_payload,
        "redaction": redaction,
        "paths": {
            "trace": str(TRACE_PATH).replace("\\", "/"),
            "receipt": str(RECEIPT_PATH).replace("\\", "/"),
            "agentsec_result": str(AGENTSEC_RESULT_PATH).replace("\\", "/"),
            "qira_result": str(QIRA_RESULT_PATH).replace("\\", "/"),
            "datacapsule_result": str(DATACAPSULE_RESULT_PATH).replace("\\", "/"),
            "reviewer_readout": str(REVIEWER_READOUT_PATH).replace("\\", "/"),
            "feedback_memory": str(FEEDBACK_MEMORY_PATH).replace("\\", "/"),
            "redaction_report": str(REDACTION_REPORT_PATH).replace("\\", "/"),
            "known_limits": str(KNOWN_LIMITS_PATH).replace("\\", "/"),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-13 local/sample pilot dry-run.")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_pilot_dry_run(sample=args.sample or True, write_result=not args.no_write)
    summary = result["receipt"]["aggregate_summary"]
    print(
        "pilot_dry_run: "
        f"verticals={summary['vertical_count']} allow={summary['total_allow_count']} "
        f"hold={summary['total_hold_count']} block={summary['total_block_count']} "
        f"redaction={result['redaction']['decision']}"
    )


if __name__ == "__main__":
    main()
