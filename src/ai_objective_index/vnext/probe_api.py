from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .objective_router import route_objective
from .objective_router_models import ObjectiveRouteRequest
from .probe_card import ProbePlan
from .probe_receipt_store import ProbeReceiptStore
from .probe_route_adapter import build_probe_plan_for_route, route_objective_with_probes
from .probe_runner import run_probe_plan


router = APIRouter(tags=["vnext-probes"])


def _store() -> ProbeReceiptStore:
    return ProbeReceiptStore()


@router.get("/v1/probes/status")
def get_probe_status() -> dict[str, Any]:
    store = _store()
    return {
        "schema": "AOI_ProbeStatus/v0.1",
        "read_only": True,
        "local_probe_only": True,
        "network": False,
        "external_tool_execution": False,
        "live_mcp_call": False,
        "gateway_execution": False,
        "probe_store_path": str(store.receipt_path),
        "claim_boundaries": [
            "local probes are not verification",
            "not security certified",
            "not a quality guarantee",
            "no action authorization",
            "no payment, booking, login, email, purchase, or contract actions",
        ],
    }


@router.post("/v1/probes/plan")
def post_probe_plan(request: ObjectiveRouteRequest) -> dict[str, Any]:
    route_payload = route_objective(request).model_dump(mode="json", by_alias=True)
    plan = build_probe_plan_for_route(route_payload, route_request=request.model_dump(mode="json"))
    return {
        "schema": "AOI_ProbePlanResponse/v0.1",
        "probe_plan": plan.model_dump(mode="json", by_alias=True),
        "read_only": True,
        "local_probe_only": True,
        "network_used": False,
        "external_tool_execution": False,
    }


@router.post("/v1/probes/run-local")
def post_run_local_probe_plan(plan: ProbePlan, store_result: bool = Query(default=True)) -> dict[str, Any]:
    receipt = run_probe_plan(plan)
    stored = None
    if store_result:
        stored = _store().append_probe_receipt(receipt)
    return {
        "schema": "AOI_LocalProbeRunResponse/v0.1",
        "probe_receipt": receipt.model_dump(mode="json", by_alias=True),
        "stored": stored is not None,
        "read_only_external": True,
        "local_memory_write": stored is not None,
        "local_probe_only": True,
        "network_used": False,
        "external_tool_execution": False,
        "gateway_execution": False,
        "token_printed": False,
    }


@router.get("/v1/probes/{receipt_id}")
def get_probe_receipt_endpoint(receipt_id: str):
    receipt = _store().get_probe_receipt(receipt_id)
    if receipt is None:
        return JSONResponse(
            status_code=404,
            content={"error": "probe_receipt_not_found", "receipt_id": receipt_id, "read_only_external": True},
        )
    receipt.update({"read_only": True, "network_used": False, "external_tool_execution": False})
    return receipt


@router.get("/v1/capabilities/{capability_id}/probe-memory")
def get_capability_probe_memory_endpoint(capability_id: str) -> dict[str, Any]:
    payload = _store().build_capability_probe_memory(capability_id).model_dump(mode="json", by_alias=True)
    payload.update({"read_only": True, "can_verify": False, "can_certify_security": False})
    return payload


@router.post("/v1/objectives/route-with-probes")
def post_route_with_probes(
    request: ObjectiveRouteRequest,
    run_local: bool = Query(default=False),
) -> dict[str, Any]:
    return route_objective_with_probes(request, run_local_probes=run_local, store=_store())
