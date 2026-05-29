from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .pilot_intake_packet import default_forbidden_actions, pilot_must_not_claim


ConsentStatus = Literal["self_owned", "owner_provided", "sample_fixture", "insufficient", "unknown"]
RetentionPreference = Literal["keep_local_artifact", "keep_redacted_receipt_only", "delete_after_review", "unknown"]
SharePreference = Literal["private_only", "redacted_summary_allowed", "public_anonymized_allowed", "unknown"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PilotConsentRecord(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotConsentRecord/v0.1", alias="schema")
    consent_id: str
    intake_id: str
    generated_at: str = Field(default_factory=timestamp)
    consent_status: ConsentStatus = "sample_fixture"
    allowed_artifacts: list[str] = Field(default_factory=list)
    disallowed_artifacts: list[str] = Field(default_factory=lambda: ["raw secrets", "private keys", ".env files", "unredacted private datasets"])
    allowed_review_modes: list[str] = Field(default_factory=lambda: ["local_static_review", "manifest_only", "diff_only"])
    disallowed_actions: list[str] = Field(default_factory=default_forbidden_actions)
    retention_preference: RetentionPreference = "keep_redacted_receipt_only"
    share_preference: SharePreference = "private_only"
    consent_limitations: list[str] = Field(default_factory=lambda: ["owner consent does not authorize external mutation, posting, merge, deploy, upload, training, or certification claims"])
    must_not_claim: list[str] = Field(default_factory=pilot_must_not_claim)
    token_printed: bool = False


def build_consent_record(
    intake_id: str,
    consent_id: str,
    consent_status: ConsentStatus,
    allowed_artifacts: list[str],
) -> PilotConsentRecord:
    return PilotConsentRecord(
        consent_id=consent_id,
        intake_id=intake_id,
        consent_status=consent_status,
        allowed_artifacts=allowed_artifacts,
    )


def consent_record_to_jsonable(record: PilotConsentRecord) -> dict[str, Any]:
    return record.model_dump(mode="json", by_alias=True)
