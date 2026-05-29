from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


SecondRunMode = Literal["local_sample_second_run"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def second_run_claim_boundary() -> dict[str, bool]:
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


class SecondRunReceipt(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_SecondRunReceipt/v0.1", alias="schema")
    second_run_id: str
    generated_at: str = Field(default_factory=timestamp)
    source_dry_run_id: str
    feedback_packet_ids: list[str] = Field(default_factory=list)
    verticals: list[str] = Field(default_factory=lambda: ["agentsec", "qira", "datacapsule"])
    mode: SecondRunMode = "local_sample_second_run"
    input_artifacts: dict[str, list[str]] = Field(default_factory=dict)
    aggregate_summary: dict[str, Any] = Field(default_factory=dict)
    vertical_results: list[dict[str, Any]] = Field(default_factory=list)
    deltas: list[dict[str, Any]] = Field(default_factory=list)
    feedback_memory_update: dict[str, Any] = Field(default_factory=dict)
    claim_boundary: dict[str, bool] = Field(default_factory=second_run_claim_boundary)
    external_actions_performed: bool = False
    github_api_used: bool = False
    live_mcp_call_used: bool = False
    merge_deploy_publish_performed: bool = False
    upload_or_training_performed: bool = False
    token_printed: bool = False
    private_kernel_exposed: bool = False


def receipt_to_jsonable(receipt: SecondRunReceipt) -> dict[str, Any]:
    return receipt.model_dump(mode="json", by_alias=True)
