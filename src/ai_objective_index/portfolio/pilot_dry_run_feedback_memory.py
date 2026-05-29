from __future__ import annotations

from typing import Any

from .pilot_dry_run_receipt import PilotDryRunFeedbackMemory, PilotDryRunResult, to_jsonable


def build_dry_run_feedback_memory(dry_run_id: str, results: list[PilotDryRunResult]) -> PilotDryRunFeedbackMemory:
    entries: list[dict[str, Any]] = []
    for result in results:
        entries.append(
            {
                "vertical": result.vertical,
                "intake_id": result.intake_id,
                "receipt_id": result.receipt_path,
                "feedback_status": "pending",
                "follow_up_actions": [
                    "request an owner-provided local artifact before a real local pilot",
                    "rerun redaction before packaging another receipt",
                    "keep HOLD/BLOCK findings in the next reviewer readout",
                ],
                "should_request_owner_artifact": True,
                "should_add_negative_control": result.block_count > 0,
                "should_add_fixture": True,
                "should_update_claim_boundary": False,
            }
        )
    return PilotDryRunFeedbackMemory(
        dry_run_id=dry_run_id,
        vertical_entries=entries,
        portfolio_next_actions=[
            "owner-consented real local artifact pilot",
            "second-run receipt",
            "unified dashboard",
            "pilot feedback form",
            "AOI MCP Registry recovery backlog",
        ],
    )


def feedback_memory_to_jsonable(memory: PilotDryRunFeedbackMemory) -> dict[str, Any]:
    return to_jsonable(memory)
