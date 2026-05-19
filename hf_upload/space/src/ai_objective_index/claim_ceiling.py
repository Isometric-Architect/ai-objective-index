from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel

from .models import ActionObject, SourceTrace


class ClaimCeiling(str, Enum):
    SAMPLE_BENCHMARK_ONLY = "SAMPLE_BENCHMARK_ONLY"
    EXTRACTED_UNVERIFIED = "EXTRACTED_UNVERIFIED"
    SOURCE_TRACED_READOUT = "SOURCE_TRACED_READOUT"
    CLAIMED_BY_SUPPLIER = "CLAIMED_BY_SUPPLIER"
    VERIFIED_OBJECT = "VERIFIED_OBJECT"
    ACTION_READY = "ACTION_READY"
    BLOCKED = "BLOCKED"


def _status(action_object: ActionObject) -> str:
    return str(action_object.status.value if hasattr(action_object.status, "value") else action_object.status).upper()


def infer_claim_ceiling(action_object: ActionObject, traces: list[SourceTrace] | None = None) -> ClaimCeiling:
    status = _status(action_object)
    categories = {str(item).lower() for item in action_object.categories}
    object_id = action_object.object_id.lower()

    if status == "BLOCKED":
        return ClaimCeiling.BLOCKED
    if status == "ACTION_READY":
        return ClaimCeiling.ACTION_READY
    if status == "VERIFIED":
        return ClaimCeiling.VERIFIED_OBJECT
    if status == "CLAIMED":
        return ClaimCeiling.CLAIMED_BY_SUPPLIER
    if status in {"DISCOVERED", "EXTRACTED", "UNVERIFIED", "EXTRACTED_UNVERIFIED", "NEEDS_REVIEW"}:
        return ClaimCeiling.EXTRACTED_UNVERIFIED
    if "fixture" in categories or "generated" in categories or object_id.endswith("_fixture"):
        return ClaimCeiling.EXTRACTED_UNVERIFIED
    if traces:
        return ClaimCeiling.SOURCE_TRACED_READOUT
    return ClaimCeiling.SAMPLE_BENCHMARK_ONLY


def claim_ceiling_not_asserted_list(claim_ceiling: ClaimCeiling | str) -> list[str]:
    ceiling = claim_ceiling.value if isinstance(claim_ceiling, ClaimCeiling) else str(claim_ceiling)
    base = [
        "not a quality guarantee",
        "not legal, financial, medical, purchasing, procurement, compliance, or professional advice",
        "not permission to buy, book, pay, log in, submit forms, email, connect accounts, purchase, or sign contracts",
    ]
    if ceiling in {ClaimCeiling.SAMPLE_BENCHMARK_ONLY.value, ClaimCeiling.EXTRACTED_UNVERIFIED.value}:
        base.append("not supplier-verified data")
    if ceiling == ClaimCeiling.EXTRACTED_UNVERIFIED.value:
        base.append("extracted price or policy fields are not legal guarantees")
    if ceiling == ClaimCeiling.SOURCE_TRACED_READOUT.value:
        base.append("source traces support fields but do not prove completeness or current truth")
    if ceiling == ClaimCeiling.BLOCKED.value:
        base.append("blocked object must not be promoted")
    return base


def enforce_claim_ceiling(score_or_receipt: Any) -> dict[str, Any]:
    if isinstance(score_or_receipt, BaseModel):
        payload = score_or_receipt.model_dump(mode="json")
    else:
        payload = dict(score_or_receipt)
    ceiling = payload.get("claim_ceiling") or ClaimCeiling.SAMPLE_BENCHMARK_ONLY.value
    payload["claim_ceiling"] = ceiling
    payload["not_asserted"] = list(
        dict.fromkeys([*payload.get("not_asserted", []), *claim_ceiling_not_asserted_list(ceiling)])
    )
    return payload
