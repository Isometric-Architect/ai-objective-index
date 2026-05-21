from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .execution_receipt_loop import ExecutionReceiptSubmission
from .execution_receipt_store import ExecutionReceiptStore
from .execution_receipt_validation import validate_execution_receipt
from .objective_router_models import ObjectiveRouteRequest
from .receipt_router_adapter import route_objective_with_receipts


router = APIRouter(tags=["vnext-execution-receipts"])


def _store() -> ExecutionReceiptStore:
    return ExecutionReceiptStore()


@router.get("/v1/execution-receipts/status")
def get_execution_receipt_status() -> dict[str, Any]:
    store = _store()
    return {
        "schema": "AOI_ExecutionReceiptStatus/v0.1",
        "read_only": True,
        "read_only_external": True,
        "local_memory_write_available": True,
        "external_execution": False,
        "probe_execution": False,
        "gateway_execution": False,
        "receipt_store_path": str(store.receipt_path),
        "claim_boundaries": [
            "receipt memory is not verification",
            "not security certified",
            "not a quality guarantee",
            "no action authorization",
            "no payment, booking, login, email, purchase, or contract actions",
        ],
    }


@router.post("/v1/execution-receipts")
def post_execution_receipt(
    request: ExecutionReceiptSubmission,
    store_rejected: bool = Query(default=False),
) -> dict[str, Any]:
    validation = validate_execution_receipt(request)
    stored = None
    if validation.valid and (not validation.decision.startswith("BLOCK")):
        stored = _store().append_receipt(request, validation).model_dump(mode="json", by_alias=True)
    elif store_rejected:
        stored = _store().append_receipt(request, validation).model_dump(mode="json", by_alias=True)
    return {
        "schema": "AOI_ExecutionReceiptSubmitResponse/v0.1",
        "receipt_id": request.receipt_id,
        "stored": stored is not None,
        "receipt": stored["receipt"] if stored else request.model_dump(mode="json", by_alias=True),
        "validation": validation.model_dump(mode="json", by_alias=True),
        "read_only_external": True,
        "local_memory_write": stored is not None,
        "external_execution": False,
        "probe_execution": False,
        "gateway_execution": False,
        "token_printed": False,
    }


@router.get("/v1/execution-receipts/{receipt_id}")
def get_execution_receipt_endpoint(receipt_id: str):
    receipt = _store().get_receipt(receipt_id)
    if receipt is None:
        return JSONResponse(
            status_code=404,
            content={"error": "receipt_not_found", "receipt_id": receipt_id, "read_only_external": True},
        )
    return receipt


@router.get("/v1/capabilities/{capability_id}/execution-receipts")
def list_capability_execution_receipts(
    capability_id: str,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    receipts = _store().list_receipts(capability_id=capability_id, limit=limit)
    return {
        "schema": "AOI_CapabilityExecutionReceiptsResponse/v0.1",
        "capability_id": capability_id,
        "receipts": receipts,
        "receipt_count": len(receipts),
        "read_only_external": True,
        "external_execution": False,
    }


@router.get("/v1/capabilities/{capability_id}/receipt-memory")
def get_capability_receipt_memory_endpoint(capability_id: str) -> dict[str, Any]:
    return _store().summarize_by_capability(capability_id)


@router.get("/v1/objectives/{objective_id}/receipt-summary")
def get_objective_receipt_summary_endpoint(objective_id: str) -> dict[str, Any]:
    return _store().summarize_by_objective(objective_id)


@router.post("/v1/objectives/route-with-receipts")
def post_route_with_receipts(request: ObjectiveRouteRequest) -> dict[str, Any]:
    return route_objective_with_receipts(request, store=_store())

