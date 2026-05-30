from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .feedback_second_run_bridge import AGENTSEC_RESULT_PATH, BRIDGE_ID, build_agentsec_feedback_second_run_result
from .feedback_second_run_candidate_selector import (
    SELECTION_REPORT_PATH,
    load_feedback_second_run_candidates,
    select_feedback_second_run_candidates,
    selection_report_to_jsonable,
    write_selection_report,
)
from .feedback_second_run_memory_update import build_memory_update, memory_update_to_jsonable
from .feedback_second_run_readout import build_feedback_second_run_readout
from .feedback_second_run_receipt import FeedbackSecondRunReceipt, claim_boundary, receipt_to_jsonable
from .feedback_second_run_redaction import REDACTION_REPORT_PATH, scan_feedback_second_run_artifacts
from .feedback_second_run_skipped import build_skipped_report, skipped_report_to_jsonable
from .feedback_second_run_trace import build_bridge_trace, trace_to_jsonable


OUTPUT_DIR = Path("feedback_second_runs")
TRACE_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_TRACE.json"
RECEIPT_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_RECEIPT.json"
SKIPPED_QIRA_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_SKIPPED_QIRA.json"
SKIPPED_DATACAPSULE_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_SKIPPED_DATACAPSULE.json"
SKIPPED_PORTFOLIO_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_SKIPPED_PORTFOLIO.json"
MEMORY_UPDATE_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_MEMORY_UPDATE.json"
REVIEWER_READOUT_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_REVIEWER_READOUT.md"
KNOWN_LIMITS_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_KNOWN_LIMITS.md"

SKIPPED_PATHS = {
    "qira": SKIPPED_QIRA_PATH,
    "datacapsule": SKIPPED_DATACAPSULE_PATH,
    "portfolio": SKIPPED_PORTFOLIO_PATH,
}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _known_limits() -> str:
    return """# ROE-20 Feedback Second-Run Known Limits

- Local/sample feedback candidates only.
- Only READY_FOR_LOCAL_SECOND_RUN candidates execute.
- HOLD candidates are skipped with retry notes until local redacted artifacts or clearer context arrive.
- No GitHub API calls, issue/PR/comment creation, cloning, URL fetching, crawling, live MCP/tool calls, external repository mutation, posting, merge, deploy, package publishing, upload, model training, credential use, or token handling.
- No HOLD/BLOCK to ALLOW upgrade is performed.
- Not an external pilot.
- Not security certification.
- Not code correctness proof.
- Not legal, privacy, license, or eval-clean proof.
- Not a quality guarantee.
- Not product readiness.
- No external action authorization.
"""


def _selected_result(candidate: dict[str, Any]) -> dict[str, Any]:
    vertical = str(candidate.get("vertical", "unknown"))
    if vertical != "agentsec":
        raise ValueError(f"ROE-20 sample bridge can only execute the ready AgentSec candidate, got {vertical!r}")
    return build_agentsec_feedback_second_run_result(candidate)


def run_feedback_second_run_bridge(sample: bool = True, write_result: bool = True) -> dict[str, Any]:
    candidates = load_feedback_second_run_candidates(ensure_replies=sample)
    selection = select_feedback_second_run_candidates(candidates)
    selection_payload = write_selection_report(selection) if write_result else selection_report_to_jsonable(selection)

    executed_results = [_selected_result(candidate) for candidate in selection.selected_candidates]
    skipped_reports = [skipped_report_to_jsonable(build_skipped_report(candidate)) for candidate in selection.skipped_candidates]

    memory_update = memory_update_to_jsonable(build_memory_update(BRIDGE_ID, executed_results, skipped_reports))
    trace = trace_to_jsonable(build_bridge_trace(selection_payload, executed_results, skipped_reports))

    new_allow = sum(int(result.get("new_decision_summary", {}).get("allow_count", 0) or 0) for result in executed_results)
    new_hold = sum(int(result.get("new_decision_summary", {}).get("hold_count", 0) or 0) for result in executed_results)
    new_block = sum(int(result.get("new_decision_summary", {}).get("block_count", 0) or 0) for result in executed_results)
    finding_updates = sum(len(result.get("finding_updates", [])) for result in executed_results)
    fixture_candidates = sum(len(result.get("fixture_candidates", [])) for result in executed_results)
    negative_control_candidates = sum(len(result.get("negative_control_candidates", [])) for result in executed_results)
    receipt = receipt_to_jsonable(
        FeedbackSecondRunReceipt(
            bridge_id=BRIDGE_ID,
            selected_results=executed_results,
            skipped_reports=skipped_reports,
            aggregate_summary={
                "selected_count": len(selection.selected_candidates),
                "skipped_count": len(selection.skipped_candidates),
                "executed_count": len(executed_results),
                "new_allow_count": new_allow,
                "new_hold_count": new_hold,
                "new_block_count": new_block,
                "finding_updates_count": finding_updates,
                "fixture_candidate_count": fixture_candidates,
                "negative_control_candidate_count": negative_control_candidates,
                "external_action_count": 0,
            },
            memory_update=memory_update,
            claim_boundary=claim_boundary(),
        )
    )
    readout = build_feedback_second_run_readout(receipt, selection_payload)

    artifact_paths = [
        SELECTION_REPORT_PATH,
        TRACE_PATH,
        RECEIPT_PATH,
        AGENTSEC_RESULT_PATH,
        *SKIPPED_PATHS.values(),
        MEMORY_UPDATE_PATH,
        REVIEWER_READOUT_PATH,
        KNOWN_LIMITS_PATH,
    ]
    if write_result:
        _write_json(TRACE_PATH, trace)
        _write_json(AGENTSEC_RESULT_PATH, executed_results[0] if executed_results else {})
        for report in skipped_reports:
            path = SKIPPED_PATHS.get(str(report.get("vertical", "")).lower(), OUTPUT_DIR / f"ROE20_FEEDBACK_SECOND_RUN_SKIPPED_{str(report.get('vertical', 'UNKNOWN')).upper()}.json")
            _write_json(path, report)
        _write_json(MEMORY_UPDATE_PATH, memory_update)
        _write_json(RECEIPT_PATH, receipt)
        _write_text(REVIEWER_READOUT_PATH, readout)
        _write_text(KNOWN_LIMITS_PATH, _known_limits())

    redaction = scan_feedback_second_run_artifacts(artifact_paths, write_result=write_result)
    return {
        "selection_report": selection_payload,
        "trace": trace,
        "selected_results": executed_results,
        "skipped_reports": skipped_reports,
        "memory_update": memory_update,
        "receipt": receipt,
        "readout": readout,
        "redaction": redaction,
        "artifact_paths": [str(path).replace("\\", "/") for path in [*artifact_paths, REDACTION_REPORT_PATH]],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-20 local feedback-to-second-run bridge.")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_feedback_second_run_bridge(sample=args.sample or True, write_result=not args.no_write)
    summary = result["receipt"].get("aggregate_summary", {})
    print(
        "feedback_second_run_executor: "
        f"selected={summary.get('selected_count', 0)} skipped={summary.get('skipped_count', 0)} "
        f"executed={summary.get('executed_count', 0)} redaction={result['redaction']['decision']}"
    )


if __name__ == "__main__":
    main()
