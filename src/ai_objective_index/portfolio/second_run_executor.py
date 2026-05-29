from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_feedback_form import (
    AGENTSEC_PACKET_PATH,
    CLASSIFICATION_SAMPLE_PATH,
    DATACAPSULE_PACKET_PATH,
    QIRA_PACKET_PATH,
    SECOND_RUN_PLAN_SAMPLE_PATH,
    package_pilot_feedback,
)
from .second_run_artifact_index import ARTIFACT_INDEX_PATH, build_second_run_artifact_index
from .second_run_delta import build_delta_from_result, delta_to_jsonable
from .second_run_feedback_memory import build_second_run_feedback_memory, feedback_memory_to_jsonable
from .second_run_readout import build_second_run_readout
from .second_run_receipt import SecondRunReceipt, receipt_to_jsonable
from .second_run_redaction import REDACTION_REPORT_PATH, scan_second_run_artifacts


SECOND_RUN_DIR = Path("pilot_second_runs")
RECEIPT_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_RECEIPT.json"
AGENTSEC_RESULT_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_RESULT_AGENTSEC.json"
QIRA_RESULT_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_RESULT_QIRA.json"
DATACAPSULE_RESULT_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_RESULT_DATACAPSULE.json"
AGENTSEC_DELTA_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_DELTA_AGENTSEC.json"
QIRA_DELTA_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_DELTA_QIRA.json"
DATACAPSULE_DELTA_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_DELTA_DATACAPSULE.json"
FEEDBACK_MEMORY_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_FEEDBACK_MEMORY.json"
REVIEWER_READOUT_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_REVIEWER_READOUT.md"
KNOWN_LIMITS_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_KNOWN_LIMITS.md"

PRIOR_RECEIPTS = {
    "agentsec": Path("pilot_receipts") / "agentsec" / "AGENTSEC_PILOT_RECEIPT_SAMPLE.json",
    "qira": Path("pilot_receipts") / "qira" / "QIRA_PILOT_RECEIPT_SAMPLE.json",
    "datacapsule": Path("pilot_receipts") / "datacapsule" / "DATACAPSULE_PILOT_RECEIPT_SAMPLE.json",
}
RESULT_PATHS = {
    "agentsec": AGENTSEC_RESULT_PATH,
    "qira": QIRA_RESULT_PATH,
    "datacapsule": DATACAPSULE_RESULT_PATH,
}
DELTA_PATHS = {
    "agentsec": AGENTSEC_DELTA_PATH,
    "qira": QIRA_DELTA_PATH,
    "datacapsule": DATACAPSULE_DELTA_PATH,
}


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
    payload = json.loads(full.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _counts(receipt: dict[str, Any]) -> dict[str, int]:
    summary = receipt.get("decision_summary", {}) if isinstance(receipt, dict) else {}
    return {
        "allow_count": int(summary.get("allow_count", 0) or 0),
        "hold_count": int(summary.get("hold_count", 0) or 0),
        "block_count": int(summary.get("block_count", 0) or 0),
    }


def _primary_decision(vertical: str) -> str:
    return {
        "agentsec": "BLOCK_FORBIDDEN_ACTION",
        "qira": "BLOCK_RELEASE_SIDE_EFFECT",
        "datacapsule": "BLOCK_ACTION_USE",
    }.get(vertical, "HOLD_REVIEW")


def _feedback_lookup() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    package_pilot_feedback(sample=True)
    packets = {
        payload.get("vertical"): payload
        for payload in [_read_json(AGENTSEC_PACKET_PATH), _read_json(QIRA_PACKET_PATH), _read_json(DATACAPSULE_PACKET_PATH)]
        if payload.get("vertical")
    }
    classifications = {
        item.get("affected_verticals", ["unknown"])[0]: item
        for item in _read_json(CLASSIFICATION_SAMPLE_PATH).get("classifications", [])
        if isinstance(item, dict) and item.get("affected_verticals")
    }
    plans = {
        item.get("verticals_to_rerun", ["unknown"])[0]: item
        for item in _read_json(SECOND_RUN_PLAN_SAMPLE_PATH).get("plans", [])
        if isinstance(item, dict) and item.get("verticals_to_rerun")
    }
    return packets, classifications, plans


def build_known_limits() -> str:
    return """# ROE-15 Second-Run Known Limits

- Local/sample artifacts only.
- No external pilot occurred.
- No GitHub API calls, issue/PR/comment creation, cloning, URL fetching, crawling, live MCP/tool calls, external repo mutation, merge, deploy, package publishing, upload, model training, credential use, or token handling.
- No raw private-data inspection.
- Decision changes are conservative; no BLOCK->ALLOW or HOLD->ALLOW upgrade is performed.
- Not security certification.
- Not code correctness proof.
- Not legal, privacy, license, or eval-clean proof.
- Not a quality guarantee.
- Not product readiness.
- No external action authorization.
"""


def _updated_result(vertical: str, prior: dict[str, Any], feedback: dict[str, Any], classification: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    counts = _counts(prior)
    updated_receipt = copy.deepcopy(prior)
    feedback_id = feedback.get("feedback_id", f"feedback-{vertical}")
    fixture_candidates: list[dict[str, Any]] = []
    negative_control_candidates: list[dict[str, Any]] = []
    requires_followup = False
    updated_next_actions = [
        "keep second-run artifact local/offline",
        "preserve claim boundaries",
        "do not post, merge, deploy, publish, fetch, clone, upload, train, or call external APIs",
    ]

    if vertical == "agentsec":
        finding_id = "agentsec-pilot-finding-2"
        prior_explanation = "permission-scope finding needed a clearer manifest-only explanation"
        updated_explanation = "Second-run feedback clarified that permission-scope HOLD means metadata requires owner review before any use; it is not a security certification or live tool result."
        incorporation_summary = "Clarified the permission-scope explanation and kept the HOLD/BLOCK counts unchanged."
        updated_next_actions.append("request owner-maintained permission scope notes for any real local pilot")
    elif vertical == "qira":
        finding_id = "qira-pilot-finding-2"
        prior_explanation = "CI evidence gap remained partial"
        updated_explanation = "Second-run feedback converted the CI evidence gap into an explicit request for a redacted local CI summary before any future receipt decision change."
        incorporation_summary = "Recorded the CI evidence request and kept release-side-effect BLOCK unchanged."
        requires_followup = True
        updated_next_actions.append("request redacted local CI evidence before rerunning QIRA on an owner artifact")
    else:
        finding_id = "datacapsule-pilot-finding-3"
        prior_explanation = "action-use BLOCK was already present"
        updated_explanation = "Second-run feedback added an explicit action-use denial fixture candidate while preserving the action-use BLOCK."
        incorporation_summary = "Added a fixture candidate for explicit action-use denial and kept action use blocked."
        fixture_candidates.append(
            {
                "fixture_id": "datacapsule-action-use-denial-candidate-v0-1",
                "source_feedback_id": feedback_id,
                "purpose": "exercise explicit action-use denial while staying manifest-only",
                "raw_data_included": False,
            }
        )
        updated_next_actions.append("add action-use denial fixture to future DataCapsule local fixture corpus")

    finding_updates = [
        {
            "finding_id": finding_id,
            "prior_explanation": prior_explanation,
            "updated_explanation": updated_explanation,
            "decision_changed": False,
        }
    ]
    updated_receipt["second_run_update"] = {
        "feedback_id": feedback_id,
        "classification": classification.get("classification", "UNKNOWN"),
        "plan_status": plan.get("run_status", "UNKNOWN"),
        "finding_updates": finding_updates,
        "fixture_candidates": fixture_candidates,
        "negative_control_candidates": negative_control_candidates,
        "updated_next_actions": updated_next_actions,
        "decision_upgrade_performed": False,
    }
    updated_receipt["decision_summary"] = {
        **counts,
        "top_hold_reasons": prior.get("decision_summary", {}).get("top_hold_reasons", []),
        "top_block_reasons": prior.get("decision_summary", {}).get("top_block_reasons", []),
    }
    result_path = RESULT_PATHS[vertical]
    return {
        "schema": "ResidualOps_SecondRunVerticalResult/v0.1",
        "second_run_id": "roe15-local-sample-second-run-v0-1",
        "vertical": vertical,
        "feedback_id": feedback_id,
        "classification": classification.get("classification", "UNKNOWN"),
        "plan_status": plan.get("run_status", "UNKNOWN"),
        "prior_receipt_ref": str(PRIOR_RECEIPTS[vertical]).replace("\\", "/"),
        "new_receipt_ref": str(result_path).replace("\\", "/"),
        "prior_decision_summary": counts,
        "new_decision_summary": counts,
        "primary_decision": _primary_decision(vertical),
        "finding_updates": finding_updates,
        "unchanged_findings": [
            finding.get("finding_id", "")
            for finding in prior.get("findings", [])
            if finding.get("finding_id") != finding_id
        ],
        "fixture_candidates": fixture_candidates,
        "negative_control_candidates": negative_control_candidates,
        "claim_boundary_changes": [],
        "updated_next_actions": updated_next_actions,
        "incorporation_summary": incorporation_summary,
        "requires_followup": requires_followup,
        "updated_receipt": updated_receipt,
        "external_actions_performed": False,
        "github_api_used": False,
        "live_mcp_call_used": False,
        "merge_deploy_publish_performed": False,
        "upload_or_training_performed": False,
        "external_action_authorized": False,
        "certification_upgrade_detected": False,
        "decision_upgrade_performed": False,
    }


def run_second_run(sample: bool = True, write_result: bool = True) -> dict[str, Any]:
    second_run_id = "roe15-local-sample-second-run-v0-1"
    feedback_packets, classifications, plans = _feedback_lookup()
    vertical_results: list[dict[str, Any]] = []
    deltas: list[dict[str, Any]] = []
    for vertical in ["agentsec", "qira", "datacapsule"]:
        prior = _read_json(PRIOR_RECEIPTS[vertical])
        result = _updated_result(vertical, prior, feedback_packets.get(vertical, {}), classifications.get(vertical, {}), plans.get(vertical, {}))
        delta = delta_to_jsonable(build_delta_from_result(result))
        vertical_results.append(result)
        deltas.append(delta)
        if write_result:
            _write_json(RESULT_PATHS[vertical], result)
            _write_json(DELTA_PATHS[vertical], delta)

    feedback_memory = build_second_run_feedback_memory(second_run_id, vertical_results)
    feedback_memory_payload = feedback_memory_to_jsonable(feedback_memory)
    prior_allow = sum(result["prior_decision_summary"]["allow_count"] for result in vertical_results)
    prior_hold = sum(result["prior_decision_summary"]["hold_count"] for result in vertical_results)
    prior_block = sum(result["prior_decision_summary"]["block_count"] for result in vertical_results)
    new_allow = sum(result["new_decision_summary"]["allow_count"] for result in vertical_results)
    new_hold = sum(result["new_decision_summary"]["hold_count"] for result in vertical_results)
    new_block = sum(result["new_decision_summary"]["block_count"] for result in vertical_results)
    receipt = SecondRunReceipt(
        second_run_id=second_run_id,
        source_dry_run_id="roe13-local-sample-dry-run-v0-1",
        feedback_packet_ids=[result["feedback_id"] for result in vertical_results],
        input_artifacts={
            "feedback_packets": [
                str(AGENTSEC_PACKET_PATH).replace("\\", "/"),
                str(QIRA_PACKET_PATH).replace("\\", "/"),
                str(DATACAPSULE_PACKET_PATH).replace("\\", "/"),
            ],
            "second_run_plans": [str(SECOND_RUN_PLAN_SAMPLE_PATH).replace("\\", "/")],
            "prior_receipts": [str(path).replace("\\", "/") for path in PRIOR_RECEIPTS.values()],
        },
        aggregate_summary={
            "vertical_count": len(vertical_results),
            "prior_allow_count": prior_allow,
            "prior_hold_count": prior_hold,
            "prior_block_count": prior_block,
            "new_allow_count": new_allow,
            "new_hold_count": new_hold,
            "new_block_count": new_block,
            "finding_updates_count": sum(len(result["finding_updates"]) for result in vertical_results),
            "fixture_candidate_count": sum(len(result["fixture_candidates"]) for result in vertical_results),
            "negative_control_candidate_count": sum(len(result["negative_control_candidates"]) for result in vertical_results),
            "claim_boundary_change_count": sum(len(result["claim_boundary_changes"]) for result in vertical_results),
            "external_action_count": 0,
        },
        vertical_results=vertical_results,
        deltas=deltas,
        feedback_memory_update=feedback_memory_payload,
    )
    receipt_payload = receipt_to_jsonable(receipt)
    core_paths = [
        AGENTSEC_RESULT_PATH,
        QIRA_RESULT_PATH,
        DATACAPSULE_RESULT_PATH,
        AGENTSEC_DELTA_PATH,
        QIRA_DELTA_PATH,
        DATACAPSULE_DELTA_PATH,
        FEEDBACK_MEMORY_PATH,
        RECEIPT_PATH,
        REVIEWER_READOUT_PATH,
        KNOWN_LIMITS_PATH,
    ]
    if write_result:
        _write_json(FEEDBACK_MEMORY_PATH, feedback_memory_payload)
        _write_json(RECEIPT_PATH, receipt_payload)
        _write_text(REVIEWER_READOUT_PATH, build_second_run_readout(receipt_payload))
        _write_text(KNOWN_LIMITS_PATH, build_known_limits())
    redaction = scan_second_run_artifacts(core_paths, write_result=write_result)
    artifact_index = build_second_run_artifact_index(core_paths + [REDACTION_REPORT_PATH], write_result=write_result)
    return {
        "receipt": receipt_payload,
        "vertical_results": vertical_results,
        "deltas": deltas,
        "feedback_memory": feedback_memory_payload,
        "redaction": redaction,
        "artifact_index": artifact_index,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute the ROE-15 local/sample second-run receipt packager.")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_second_run(sample=args.sample or True, write_result=not args.no_write)
    summary = result["receipt"]["aggregate_summary"]
    print(
        "second_run_executor: "
        f"verticals={summary['vertical_count']} prior={summary['prior_allow_count']}/{summary['prior_hold_count']}/{summary['prior_block_count']} "
        f"new={summary['new_allow_count']}/{summary['new_hold_count']}/{summary['new_block_count']} "
        f"redaction={result['redaction']['decision']}"
    )


if __name__ == "__main__":
    main()
