from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Mode = Literal["local_feedback_second_run"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def claim_boundary() -> dict[str, bool]:
    return {
        "not_external_pilot": True,
        "not_security_certification": True,
        "not_code_correctness_proof": True,
        "not_legal_opinion": True,
        "not_privacy_audit": True,
        "not_license_clearance": True,
        "not_eval_clean_proof": True,
        "not_quality_guarantee": True,
        "not_product_ready": True,
        "no_external_action_authorization": True,
    }


class FeedbackSecondRunReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackSecondRunReceipt/v0.1", alias="schema")
    bridge_id: str
    generated_at: str = Field(default_factory=timestamp)
    mode: Mode = "local_feedback_second_run"
    selected_results: list[dict[str, Any]] = Field(default_factory=list)
    skipped_reports: list[dict[str, Any]] = Field(default_factory=list)
    aggregate_summary: dict[str, Any] = Field(default_factory=dict)
    memory_update: dict[str, Any] = Field(default_factory=dict)
    claim_boundary: dict[str, bool] = Field(default_factory=claim_boundary)
    external_actions_performed: bool = False
    github_api_used: bool = False
    live_mcp_call_used: bool = False
    merge_deploy_publish_performed: bool = False
    upload_or_training_performed: bool = False
    token_printed: bool = False
    private_kernel_exposed: bool = False


def receipt_to_jsonable(receipt: FeedbackSecondRunReceipt) -> dict[str, Any]:
    return receipt.model_dump(mode="json", by_alias=True)
