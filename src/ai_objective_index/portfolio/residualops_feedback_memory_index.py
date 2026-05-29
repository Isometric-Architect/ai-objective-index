from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .residualops_portfolio_loader import load_all_pilot_receipts


FEEDBACK_INDEX_PATH = Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_FEEDBACK_MEMORY_INDEX.json"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_feedback_memory_index(loaded: dict[str, Any] | None = None) -> dict[str, Any]:
    loaded = loaded or load_all_pilot_receipts()
    entries = []
    for vertical in loaded["verticals"]:
        memory = vertical.get("feedback_memory", {})
        entries.append(
            {
                "vertical": vertical["name"],
                "vertical_id": vertical["vertical_id"],
                "pilot_id": memory.get("pilot_id") or vertical.get("receipt", {}).get("pilot_id", ""),
                "feedback_status": memory.get("feedback_status", "unknown"),
                "follow_up_actions": memory.get("follow_up_actions", []),
                "should_add_negative_control": bool(memory.get("should_add_negative_control", False)),
                "should_add_fixture": bool(memory.get("should_add_fixture", False)),
                "should_update_policy_or_contract": bool(
                    memory.get("should_update_policy_profile", False)
                    or memory.get("should_update_behavior_contract", False)
                    or memory.get("should_update_manifest_schema", False)
                ),
                "should_request_evidence": bool(
                    memory.get("should_request_ci_evidence", False)
                    or memory.get("should_request_license_evidence", False)
                    or memory.get("should_request_privacy_evidence", False)
                    or memory.get("should_request_eval_split_evidence", False)
                ),
                "claim_boundary_change_needed": bool(memory.get("should_change_claim_boundary", False)),
            }
        )
    return {
        "schema": "ResidualOps_FeedbackMemoryIndex/v0.1",
        "index_id": "residualops-feedback-memory-index-v0-1",
        "generated_at": _timestamp(),
        "entry_count": len(entries),
        "entries": entries,
        "portfolio_next_actions": [
            "add owner-consented pilot intake",
            "add second-run receipt",
            "add unified dashboard",
            "add pilot feedback form",
            "keep private kernels private",
        ],
        "external_posting_performed": False,
        "external_network_used": False,
        "token_printed": False,
    }


def write_feedback_memory_index(loaded: dict[str, Any] | None = None) -> dict[str, Any]:
    index = build_feedback_memory_index(loaded)
    _write_json(FEEDBACK_INDEX_PATH, index)
    return index
