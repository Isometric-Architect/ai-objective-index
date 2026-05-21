from __future__ import annotations

from typing import Any

from .execution_receipt_loop import ExecutionReceiptSubmission
from .execution_receipt_store import ExecutionReceiptStore
from .execution_receipt_validation import validate_execution_receipt
from .objective_router_models import ObjectiveRouteRequest
from .receipt_router_adapter import route_objective_with_receipts as core_route_objective_with_receipts


def _store() -> ExecutionReceiptStore:
    return ExecutionReceiptStore()


def submit_execution_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    submission = ExecutionReceiptSubmission.model_validate(receipt)
    validation = validate_execution_receipt(submission)
    stored = None
    if validation.valid and not validation.decision.startswith("BLOCK"):
        stored = _store().append_receipt(submission, validation).model_dump(mode="json", by_alias=True)
    return {
        "schema": "AOI_MCPSubmitExecutionReceiptResult/v0.1",
        "receipt_id": submission.receipt_id,
        "stored": stored is not None,
        "validation": validation.model_dump(mode="json", by_alias=True),
        "receipt": stored["receipt"] if stored else submission.model_dump(mode="json", by_alias=True),
        "read_only": True,
        "local_memory_write": stored is not None,
        "external_execution": False,
        "probe_execution": False,
        "gateway_execution": False,
        "payment_booking_login_email_purchase_contract_actions": False,
        "verification_guarantee": False,
        "token_printed": False,
    }


def get_execution_receipt(receipt_id: str) -> dict[str, Any]:
    receipt = _store().get_receipt(receipt_id)
    if receipt is None:
        return {
            "read_only": True,
            "found": False,
            "error": "receipt_not_found",
            "receipt_id": receipt_id,
            "external_execution": False,
        }
    receipt.update({"read_only": True, "found": True, "external_execution": False})
    return receipt


def list_capability_receipts(capability_id: str, limit: int = 20) -> dict[str, Any]:
    receipts = _store().list_receipts(capability_id=capability_id, limit=limit)
    return {
        "schema": "AOI_MCPListCapabilityReceiptsResult/v0.1",
        "capability_id": capability_id,
        "receipt_count": len(receipts),
        "receipts": receipts,
        "read_only": True,
        "external_execution": False,
        "probe_execution": False,
    }


def get_capability_receipt_memory(capability_id: str) -> dict[str, Any]:
    payload = _store().summarize_by_capability(capability_id)
    payload.update(
        {
            "read_only": True,
            "external_execution": False,
            "probe_execution": False,
            "verification_guarantee": False,
        }
    )
    return payload


def route_objective_with_receipts(
    query: str,
    objective: str,
    domain: str = "mcp_servers",
    data_scope: str = "sample",
    limit: int = 10,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request = ObjectiveRouteRequest(
        query=query,
        objective=objective,
        domain=domain,
        data_scope=data_scope,  # type: ignore[arg-type]
        limit=limit,
        constraints=constraints or {},
    )
    payload = core_route_objective_with_receipts(request, store=_store())
    payload.update(
        {
            "read_only": True,
            "external_execution": False,
            "probe_execution": False,
            "gateway_execution": False,
            "verification_guarantee": False,
        }
    )
    return payload
