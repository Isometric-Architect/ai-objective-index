from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel

from .claim_ceiling import infer_claim_ceiling
from .models import ActionObject


class UseRight(str, Enum):
    READ = "READ"
    RANK = "RANK"
    COMPARE = "COMPARE"
    QUOTE = "QUOTE"
    TRAIN = "TRAIN"
    SHARE = "SHARE"
    MEMORY = "MEMORY"
    ACTION = "ACTION"


_ALLOWED = {UseRight.READ, UseRight.RANK, UseRight.COMPARE, UseRight.QUOTE}
_BLOCKED = {UseRight.TRAIN, UseRight.SHARE, UseRight.ACTION}


def _normalize(use_right: UseRight | str) -> UseRight:
    if isinstance(use_right, UseRight):
        return use_right
    return UseRight(str(use_right or "").strip().upper())


def check_use_right(action_object: ActionObject, use_right: UseRight | str) -> dict[str, Any]:
    right = _normalize(use_right)
    ceiling = infer_claim_ceiling(action_object).value
    if right in _ALLOWED:
        return {
            "use_right": right.value,
            "decision": "ALLOW",
            "claim_ceiling": ceiling,
            "reason": "AOI v0.1 allows read-only comparison and short quoted source-trace review.",
        }
    if right == UseRight.MEMORY:
        return {
            "use_right": right.value,
            "decision": "HOLD",
            "claim_ceiling": ceiling,
            "reason": "Memory use is outside AOI v0.1 default use rights.",
        }
    if right in _BLOCKED:
        return {
            "use_right": right.value,
            "decision": "BLOCK",
            "claim_ceiling": ceiling,
            "reason": "AOI v0.1 sample/generated records do not grant training, sharing, or action rights.",
        }
    return {
        "use_right": right.value,
        "decision": "HOLD",
        "claim_ceiling": ceiling,
        "reason": "Unknown use right requires review before use.",
    }


def default_use_rights_for_object(action_object: ActionObject) -> dict[str, Any]:
    return {
        right.value: check_use_right(action_object, right)
        for right in UseRight
    }


def apply_use_rights_to_decision(packet_or_receipt: Any) -> dict[str, Any]:
    payload = packet_or_receipt.model_dump(mode="json") if isinstance(packet_or_receipt, BaseModel) else dict(packet_or_receipt)
    if "use_rights" not in payload:
        payload["use_rights"] = {
            "READ": {"decision": "ALLOW"},
            "RANK": {"decision": "ALLOW"},
            "COMPARE": {"decision": "ALLOW"},
            "QUOTE": {"decision": "ALLOW"},
            "TRAIN": {"decision": "BLOCK"},
            "SHARE": {"decision": "BLOCK"},
            "MEMORY": {"decision": "HOLD"},
            "ACTION": {"decision": "BLOCK"},
        }
    return payload
