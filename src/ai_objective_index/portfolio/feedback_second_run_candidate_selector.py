from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .feedback_reply_intake import SECOND_RUN_CANDIDATE_SAMPLE_PATH, package_feedback_replies


OUTPUT_DIR = Path("feedback_second_runs")
SELECTION_REPORT_PATH = OUTPUT_DIR / "ROE20_FEEDBACK_SECOND_RUN_SELECTION_REPORT.json"


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class FeedbackSecondRunSelectionReport(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackSecondRunSelectionReport/v0.1", alias="schema")
    selection_id: str
    generated_at: str = Field(default_factory=timestamp)
    source_reply_candidates: list[dict[str, Any]] = Field(default_factory=list)
    selected_candidates: list[dict[str, Any]] = Field(default_factory=list)
    skipped_candidates: list[dict[str, Any]] = Field(default_factory=list)
    ready_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    selection_rules: list[str] = Field(
        default_factory=lambda: [
            "ready_only",
            "local_redacted_only",
            "consent_required",
            "no_external_action",
            "no_certification_upgrade",
        ]
    )
    selected_verticals: list[str] = Field(default_factory=list)
    skipped_verticals: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_feedback_second_run_candidates(ensure_replies: bool = True) -> list[dict[str, Any]]:
    if ensure_replies:
        package_feedback_replies(sample=True)
    payload = _read_json(SECOND_RUN_CANDIDATE_SAMPLE_PATH)
    return [item for item in payload.get("candidates", []) if isinstance(item, dict)]


def select_feedback_second_run_candidates(candidates: list[dict[str, Any]]) -> FeedbackSecondRunSelectionReport:
    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for candidate in candidates:
        readiness = candidate.get("readiness", "HOLD_NEEDS_ARTIFACT")
        external = bool(candidate.get("external_action_authorized", False))
        forbidden = {str(item).lower() for item in candidate.get("forbidden_operations", [])}
        requested_forbidden = any(
            action in forbidden
            for action in {
                "github_api",
                "external_posting",
                "external_repo_mutation",
                "merge",
                "deploy",
                "publish",
                "live_mcp_call",
                "upload_data",
                "train_model",
            }
        )
        if readiness == "READY_FOR_LOCAL_SECOND_RUN" and not external:
            selected.append(candidate)
        else:
            skipped_candidate = dict(candidate)
            if external or (readiness == "READY_FOR_LOCAL_SECOND_RUN" and requested_forbidden and external):
                skipped_candidate["readiness"] = "BLOCK_EXTERNAL_ACTION"
            skipped.append(skipped_candidate)
    hold_count = len([item for item in skipped if str(item.get("readiness", "")).startswith("HOLD_")])
    block_count = len([item for item in skipped if str(item.get("readiness", "")).startswith("BLOCK_")])
    return FeedbackSecondRunSelectionReport(
        selection_id="roe20-feedback-second-run-selection-v0-1",
        source_reply_candidates=candidates,
        selected_candidates=selected,
        skipped_candidates=skipped,
        ready_count=len(selected),
        hold_count=hold_count,
        block_count=block_count,
        selected_verticals=[item.get("vertical", "unknown") for item in selected],
        skipped_verticals=[item.get("vertical", "unknown") for item in skipped],
        next_actions=[
            "execute only READY_FOR_LOCAL_SECOND_RUN candidates",
            "write skipped reports for HOLD/BLOCK candidates",
            "request missing local redacted artifacts before retrying HOLD candidates",
            "do not perform external actions",
        ],
    )


def selection_report_to_jsonable(report: FeedbackSecondRunSelectionReport) -> dict[str, Any]:
    return report.model_dump(mode="json", by_alias=True)


def write_selection_report(report: FeedbackSecondRunSelectionReport) -> dict[str, Any]:
    payload = selection_report_to_jsonable(report)
    _write_json(SELECTION_REPORT_PATH, payload)
    return payload
