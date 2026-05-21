from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from .execution_receipt_loop import (
    ExecutionReceiptSubmission,
    ExecutionReceiptValidationResult,
)


FORBIDDEN_ACTION_PHRASES = [
    "payment",
    "pay ",
    "booking",
    "book ",
    "login",
    "log in",
    "email sending",
    "send email",
    "form submission",
    "submit form",
    "purchase",
    "buy ",
    "contract signing",
    "sign contract",
    "account connection",
    "connect account",
]

UNSUPPORTED_CLAIM_PHRASES = [
    "verified capability",
    "verified tool",
    "safe tool",
    "safe server",
    "security certified",
    "quality guaranteed",
    "guaranteed quality",
    "production ready",
    "production-ready",
    "external validation",
]

ACTION_AUTHORIZATION_PHRASES = [
    "action authorized",
    "authorized to act",
    "authorized purchase",
    "approved to buy",
    "permission to purchase",
    "permission to sign",
]

TOKEN_PATTERNS = [
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._-]{16,}"),
]


def _text_fields(receipt: ExecutionReceiptSubmission) -> list[str]:
    fields: list[Any] = [
        receipt.capability_name,
        receipt.outcome_summary,
        receipt.task_context,
        receipt.constraints_checked,
        receipt.observed_outputs,
        receipt.residual_notes,
        receipt.missing_fields_found,
        receipt.route_decision_before,
        receipt.route_decision_after,
    ]
    flattened: list[str] = []
    for value in fields:
        if value is None:
            continue
        if isinstance(value, list):
            flattened.extend(str(item) for item in value)
        else:
            flattened.append(str(value))
    return flattened


def contains_token_like_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in TOKEN_PATTERNS)


def redact_token_like_text(value: str) -> tuple[str, bool]:
    redacted = value
    changed = False
    for pattern in TOKEN_PATTERNS:
        redacted, count = pattern.subn("[REDACTED_TOKEN_LIKE_TEXT]", redacted)
        changed = changed or count > 0
    return redacted, changed


def receipt_contains_token_like_text(receipt: ExecutionReceiptSubmission) -> bool:
    return any(contains_token_like_text(text) for text in _text_fields(receipt))


def _contains_phrase(texts: list[str], phrases: list[str]) -> list[str]:
    lowered = "\n".join(texts).lower()
    return sorted({phrase.strip() for phrase in phrases if phrase in lowered})


def validate_execution_receipt(receipt_input: ExecutionReceiptSubmission | dict[str, Any]) -> ExecutionReceiptValidationResult:
    try:
        receipt = (
            receipt_input
            if isinstance(receipt_input, ExecutionReceiptSubmission)
            else ExecutionReceiptSubmission.model_validate(receipt_input)
        )
    except ValidationError as exc:
        return ExecutionReceiptValidationResult(
            receipt_id=str(getattr(receipt_input, "receipt_id", None) or (receipt_input or {}).get("receipt_id", "missing")),
            valid=False,
            decision="INVALID_RECEIPT",
            errors=[f"Receipt structure is invalid: {exc.errors()[0].get('msg', 'validation failed')}"],
            next_actions=["Add required receipt fields before storing receipt memory."],
        )

    errors: list[str] = []
    warnings: list[str] = []
    next_actions = ["Keep the receipt as local memory; do not treat it as verification or action authorization."]
    if not receipt.capability_id.strip():
        errors.append("capability_id is required.")
    if not receipt.outcome:
        errors.append("outcome is required.")
    if errors:
        return ExecutionReceiptValidationResult(
            receipt_id=receipt.receipt_id or "missing",
            valid=False,
            decision="INVALID_RECEIPT",
            errors=errors,
            warnings=warnings,
            next_actions=["Provide capability_id and outcome before retrying."],
        )

    texts = _text_fields(receipt)
    forbidden = _contains_phrase(texts, FORBIDDEN_ACTION_PHRASES)
    if forbidden:
        return ExecutionReceiptValidationResult(
            receipt_id=receipt.receipt_id or "missing",
            valid=False,
            decision="BLOCK_FORBIDDEN_ACTION",
            errors=[f"Forbidden external action wording detected: {', '.join(forbidden)}"],
            warnings=warnings,
            next_actions=["Remove forbidden action claims. AOI receipt memory cannot authorize external actions."],
        )

    unsupported = _contains_phrase(texts, UNSUPPORTED_CLAIM_PHRASES)
    if unsupported:
        return ExecutionReceiptValidationResult(
            receipt_id=receipt.receipt_id or "missing",
            valid=False,
            decision="BLOCK_UNSUPPORTED_CLAIM",
            errors=[f"Unsupported verification, safety, certification, or quality claim detected: {', '.join(unsupported)}"],
            warnings=warnings,
            next_actions=["Rewrite as an observed outcome with known limits, not a verification or guarantee."],
        )

    authorization = _contains_phrase(texts, ACTION_AUTHORIZATION_PHRASES)
    if authorization:
        return ExecutionReceiptValidationResult(
            receipt_id=receipt.receipt_id or "missing",
            valid=False,
            decision="BLOCK_ACTION_AUTHORIZATION",
            errors=[f"Action authorization wording detected: {', '.join(authorization)}"],
            warnings=warnings,
            next_actions=["Remove action authorization wording. Receipts do not grant permission to act."],
        )

    if receipt_contains_token_like_text(receipt):
        warnings.append("Token-like text detected; store layer should redact or block secret-like content.")

    if receipt.receipt_origin == "self_reported" and receipt.outcome == "success":
        return ExecutionReceiptValidationResult(
            receipt_id=receipt.receipt_id or "missing",
            valid=True,
            decision="HOLD_LOW_EVIDENCE_ORIGIN",
            warnings=warnings + ["Self-reported success can influence notes but cannot verify a capability."],
            can_influence_route=True,
            next_actions=next_actions + ["Collect independent source traces or benchmark receipts before stronger routing."],
        )

    if receipt.outcome in {"fail", "blocked"} and receipt.receipt_origin == "public_issue":
        warnings.append("Public issue failure can add known-failure memory, but may be incomplete.")
    if receipt.outcome == "success" and receipt.route_decision_before and receipt.route_decision_after:
        before = receipt.route_decision_before.upper()
        after = receipt.route_decision_after.upper()
        if before.startswith("HOLD") and after.startswith("ALLOW"):
            return ExecutionReceiptValidationResult(
                receipt_id=receipt.receipt_id or "missing",
                valid=True,
                decision="HOLD_CONFLICTING_OUTCOME",
                warnings=warnings + ["Receipt proposes an upgrade from HOLD to ALLOW; this MVP does not permit receipt-driven upgrades."],
                can_influence_route=True,
                next_actions=next_actions + ["Use receipt memory only as notes or downgrade signal in this package."],
            )

    return ExecutionReceiptValidationResult(
        receipt_id=receipt.receipt_id or "missing",
        valid=True,
        decision="RECEIPT_ACCEPTED",
        warnings=warnings,
        can_influence_route=True,
        next_actions=next_actions,
    )
