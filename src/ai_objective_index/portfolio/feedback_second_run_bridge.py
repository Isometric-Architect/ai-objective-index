from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


BRIDGE_ID = "roe20-feedback-second-run-bridge-v0-1"
PRIOR_AGENTSEC_RECEIPT_PATH = Path("pilot_receipts") / "agentsec" / "AGENTSEC_PILOT_RECEIPT_SAMPLE.json"
AGENTSEC_RESULT_PATH = Path("feedback_second_runs") / "ROE20_FEEDBACK_SECOND_RUN_RESULT_AGENTSEC.json"


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _decision_summary(receipt: dict[str, Any]) -> dict[str, int]:
    summary = receipt.get("decision_summary", {}) if isinstance(receipt, dict) else {}
    return {
        "allow_count": int(summary.get("allow_count", 0) or 0),
        "hold_count": int(summary.get("hold_count", 0) or 0),
        "block_count": int(summary.get("block_count", 0) or 0),
    }


def build_agentsec_feedback_second_run_result(candidate: dict[str, Any]) -> dict[str, Any]:
    prior = _read_json(PRIOR_AGENTSEC_RECEIPT_PATH)
    counts = _decision_summary(prior)
    updated_receipt = copy.deepcopy(prior)
    reply_id = str(candidate.get("reply_id", "feedback-reply-sample-agentsec-v0-1"))
    candidate_id = str(candidate.get("second_run_candidate_id", "second-run-candidate-feedback-reply-sample-agentsec-v0-1"))
    finding_update = {
        "finding_id": "agentsec-pilot-finding-2",
        "prior_explanation": "fixture.local/repo-file-review-helper: policy holds file_access",
        "updated_explanation": (
            "Feedback requested a local second pass for the AgentSec permission-scope HOLD. "
            "The second-run bridge records the clarification as a local fixture candidate and keeps "
            "the HOLD/BLOCK decisions unchanged."
        ),
        "decision_changed": False,
    }
    fixture_candidate = {
        "fixture_id": "agentsec-feedback-permission-scope-local-fixture-candidate-v0-1",
        "source_reply_id": reply_id,
        "source_candidate_id": candidate_id,
        "purpose": "exercise permission-scope clarification in a local-only second-run path",
        "raw_private_data_included": False,
    }
    updated_receipt["feedback_second_run_update"] = {
        "bridge_id": BRIDGE_ID,
        "reply_id": reply_id,
        "candidate_id": candidate_id,
        "finding_updates": [finding_update],
        "fixture_candidates": [fixture_candidate],
        "negative_control_candidates": [],
        "decision_upgrade_performed": False,
        "external_action_authorized": False,
    }
    return {
        "schema": "ResidualOps_FeedbackSecondRunVerticalResult/v0.1",
        "bridge_id": BRIDGE_ID,
        "vertical": "agentsec",
        "reply_id": reply_id,
        "second_run_candidate_id": candidate_id,
        "selected_packager": "local_agentsec_feedback_second_run_bridge",
        "prior_receipt_ref": str(PRIOR_AGENTSEC_RECEIPT_PATH).replace("\\", "/"),
        "new_receipt_ref": str(AGENTSEC_RESULT_PATH).replace("\\", "/"),
        "prior_decision_summary": counts,
        "new_decision_summary": counts,
        "allow_count": counts["allow_count"],
        "hold_count": counts["hold_count"],
        "block_count": counts["block_count"],
        "primary_decision": "BLOCK_FORBIDDEN_ACTION",
        "finding_updates": [finding_update],
        "fixture_candidates": [fixture_candidate],
        "negative_control_candidates": [],
        "decision_changes": {
            "allow_to_hold_count": 0,
            "hold_to_allow_count": 0,
            "hold_to_block_count": 0,
            "block_to_hold_count": 0,
            "block_to_allow_count": 0,
        },
        "incorporation_summary": "AgentSec feedback candidate was incorporated as a local-only clarification with no decision upgrade.",
        "known_limits": [
            "local/sample artifact only",
            "no live MCP call",
            "no external tool execution",
            "not security certification",
            "no external action authorization",
        ],
        "claim_boundary": {
            "not_external_pilot": True,
            "not_security_certification": True,
            "not_quality_guarantee": True,
            "not_product_ready": True,
            "no_external_action_authorization": True,
        },
        "external_actions_performed": False,
        "github_api_used": False,
        "live_mcp_call_used": False,
        "external_repo_modified": False,
        "posting_or_commenting_performed": False,
        "merge_deploy_publish_performed": False,
        "upload_or_training_performed": False,
        "token_used": False,
        "decision_upgrade_performed": False,
        "unsafe_decision_upgrade_detected": False,
        "certification_upgrade_detected": False,
        "external_action_authorized": False,
        "updated_receipt": updated_receipt,
    }
