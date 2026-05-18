from __future__ import annotations

from enum import Enum
from typing import Any


class ActionBoundary(str, Enum):
    READ = "READ"
    RANK = "RANK"
    COMPARE = "COMPARE"
    EXPLAIN = "EXPLAIN"
    QUOTE_SNIPPET = "QUOTE_SNIPPET"
    DECISION_RECEIPT = "DECISION_RECEIPT"
    EMAIL = "EMAIL"
    BOOK = "BOOK"
    PAY = "PAY"
    LOGIN = "LOGIN"
    SUBMIT_FORM = "SUBMIT_FORM"
    PURCHASE = "PURCHASE"
    SIGN_CONTRACT = "SIGN_CONTRACT"
    ACCOUNT_CONNECT = "ACCOUNT_CONNECT"


_ALLOWED = {
    ActionBoundary.READ.value,
    ActionBoundary.RANK.value,
    ActionBoundary.COMPARE.value,
    ActionBoundary.EXPLAIN.value,
    ActionBoundary.QUOTE_SNIPPET.value,
    ActionBoundary.DECISION_RECEIPT.value,
}

_BLOCKED = {
    ActionBoundary.EMAIL.value,
    ActionBoundary.BOOK.value,
    ActionBoundary.PAY.value,
    ActionBoundary.LOGIN.value,
    ActionBoundary.SUBMIT_FORM.value,
    ActionBoundary.PURCHASE.value,
    ActionBoundary.SIGN_CONTRACT.value,
    ActionBoundary.ACCOUNT_CONNECT.value,
}


def _normalize(action: ActionBoundary | str) -> str:
    if isinstance(action, ActionBoundary):
        return action.value
    text = str(action or "").strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "PAYMENT": "PAY",
        "BOOKING": "BOOK",
        "EMAIL_SENDING": "EMAIL",
        "FORM_SUBMISSION": "SUBMIT_FORM",
        "CONTRACT_SIGNING": "SIGN_CONTRACT",
        "ACCOUNT_CONNECTION": "ACCOUNT_CONNECT",
    }
    return aliases.get(text, text)


def check_action_boundary(action: ActionBoundary | str) -> dict[str, Any]:
    action_value = _normalize(action)
    if action_value in _ALLOWED:
        return {
            "action": action_value,
            "decision": "ALLOW",
            "read_only": True,
            "reason": "Allowed AOI v0.1 read-only operation.",
        }
    if action_value in _BLOCKED:
        return {
            "action": action_value,
            "decision": "BLOCK",
            "read_only": True,
            "reason": "AOI v0.1 blocks external actions and account-modifying operations.",
        }
    return {
        "action": action_value,
        "decision": "HOLD",
        "read_only": True,
        "reason": "Unknown action boundary; treat as hold until reviewed.",
    }


def forbidden_actions_v0_1() -> list[str]:
    return [
        "email",
        "booking",
        "payment",
        "login",
        "form_submission",
        "purchase",
        "contract_signing",
        "account_connection",
    ]


def add_action_boundary_to_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    payload = dict(receipt)
    payload["action_boundary"] = {
        "allowed_actions": sorted(_ALLOWED),
        "blocked_actions": forbidden_actions_v0_1(),
        "decision_receipt": check_action_boundary(ActionBoundary.DECISION_RECEIPT),
    }
    return payload
