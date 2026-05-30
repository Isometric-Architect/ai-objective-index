from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class FeedbackSecondRunBridgeTrace(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackSecondRunBridgeTrace/v0.1", alias="schema")
    bridge_id: str
    generated_at: str = Field(default_factory=timestamp)
    source_feedback_reply_pack: str
    selection_report_ref: str
    selected_count: int
    skipped_count: int
    executed_count: int
    local_only: bool = True
    external_network_used: bool = False
    github_api_used: bool = False
    live_mcp_call_used: bool = False
    external_repo_modified: bool = False
    posting_or_commenting_performed: bool = False
    merge_deploy_publish_performed: bool = False
    token_used: bool = False
    steps: list[dict[str, Any]] = Field(default_factory=list)


def build_bridge_trace(selection: dict[str, Any], executed_results: list[dict[str, Any]], skipped_reports: list[dict[str, Any]]) -> FeedbackSecondRunBridgeTrace:
    steps = [
        {
            "step_id": "select-ready-candidates",
            "step_name": "Select READY local candidates",
            "input_ref": "feedback_replies/FEEDBACK_REPLY_SECOND_RUN_CANDIDATE_SAMPLE.json",
            "output_ref": "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_SELECTION_REPORT.json",
            "decision": f"selected={len(executed_results)} skipped={len(skipped_reports)}",
            "notes": "READY candidates only; HOLD/BLOCK candidates skipped",
        }
    ]
    for result in executed_results:
        steps.append(
            {
                "step_id": f"execute-{result.get('vertical', 'unknown')}",
                "step_name": "Execute local feedback second-run bridge",
                "input_ref": result.get("source_candidate_id", ""),
                "output_ref": result.get("result_ref", ""),
                "decision": result.get("primary_decision", "HOLD_REVIEW"),
                "notes": "local/offline result only; no decision upgrade",
            }
        )
    for skipped in skipped_reports:
        steps.append(
            {
                "step_id": f"skip-{skipped.get('vertical', 'unknown')}",
                "step_name": "Skip non-ready candidate",
                "input_ref": skipped.get("candidate_id", ""),
                "output_ref": f"feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_SKIPPED_{skipped.get('vertical', 'unknown').upper()}.json",
                "decision": skipped.get("reason", ""),
                "notes": "candidate remains HOLD/BLOCK until local artifact or consent is available",
            }
        )
    return FeedbackSecondRunBridgeTrace(
        bridge_id="roe20-feedback-second-run-bridge-v0-1",
        source_feedback_reply_pack="feedback_replies/FEEDBACK_REPLY_SECOND_RUN_CANDIDATE_SAMPLE.json",
        selection_report_ref="feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_SELECTION_REPORT.json",
        selected_count=int(selection.get("ready_count", 0) or 0),
        skipped_count=len(skipped_reports),
        executed_count=len(executed_results),
        steps=steps,
    )


def trace_to_jsonable(trace: FeedbackSecondRunBridgeTrace) -> dict[str, Any]:
    return trace.model_dump(mode="json", by_alias=True)
