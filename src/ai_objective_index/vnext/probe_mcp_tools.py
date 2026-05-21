from __future__ import annotations

from typing import Any

from .objective_router import route_objective
from .objective_router_models import ObjectiveRouteRequest
from .probe_card import ProbePlan
from .probe_receipt_store import ProbeReceiptStore
from .probe_route_adapter import build_probe_plan_for_route, route_objective_with_probes as core_route_objective_with_probes
from .probe_runner import run_probe_plan


def _store() -> ProbeReceiptStore:
    return ProbeReceiptStore()


def plan_probe_before_use(
    query: str,
    objective: str,
    data_scope: str = "sample",
    limit: int = 5,
    domain: str = "mcp_servers",
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request = ObjectiveRouteRequest(
        query=query,
        objective=objective,
        data_scope=data_scope,  # type: ignore[arg-type]
        limit=limit,
        domain=domain,
        constraints=constraints or {},
    )
    route_payload = route_objective(request).model_dump(mode="json", by_alias=True)
    plan = build_probe_plan_for_route(route_payload, route_request=request.model_dump(mode="json"))
    return {
        "schema": "AOI_MCPPlanProbeBeforeUseResult/v0.1",
        "probe_plan": plan.model_dump(mode="json", by_alias=True),
        "read_only": True,
        "local_metadata_probes_only": True,
        "live_mcp_call": False,
        "external_tool_execution": False,
        "security_certification": False,
        "action_authorization": False,
    }


def run_local_probe_plan(plan: dict[str, Any] | None = None, plan_id: str | None = None) -> dict[str, Any]:
    if plan is None:
        return {
            "schema": "AOI_MCPRunLocalProbePlanResult/v0.1",
            "error": "plan_required",
            "plan_id": plan_id,
            "read_only": True,
            "local_probe_only": True,
            "network_used": False,
            "external_tool_execution": False,
        }
    probe_plan = ProbePlan.model_validate(plan)
    receipt = run_probe_plan(probe_plan)
    stored = _store().append_probe_receipt(receipt)
    return {
        "schema": "AOI_MCPRunLocalProbePlanResult/v0.1",
        "probe_receipt": receipt.model_dump(mode="json", by_alias=True),
        "stored": True,
        "stored_receipt": stored,
        "read_only_external": True,
        "local_memory_write": True,
        "local_probe_only": True,
        "network_used": False,
        "external_tool_execution": False,
        "security_certification": False,
        "action_authorization": False,
        "token_printed": False,
    }


def get_probe_receipt(receipt_id: str) -> dict[str, Any]:
    receipt = _store().get_probe_receipt(receipt_id)
    if receipt is None:
        return {
            "schema": "AOI_MCPGetProbeReceiptResult/v0.1",
            "found": False,
            "receipt_id": receipt_id,
            "read_only": True,
            "network_used": False,
        }
    return {
        "schema": "AOI_MCPGetProbeReceiptResult/v0.1",
        "found": True,
        "probe_receipt": receipt,
        "read_only": True,
        "network_used": False,
        "external_tool_execution": False,
    }


def get_capability_probe_memory(capability_id: str) -> dict[str, Any]:
    payload = _store().build_capability_probe_memory(capability_id).model_dump(mode="json", by_alias=True)
    payload.update(
        {
            "schema": "AOI_MCPGetCapabilityProbeMemoryResult/v0.1",
            "read_only": True,
            "local_probe_only": True,
            "can_verify": False,
            "can_certify_security": False,
            "network_used": False,
        }
    )
    return payload


def route_objective_with_probes(
    query: str,
    objective: str,
    data_scope: str = "sample",
    limit: int = 5,
    domain: str = "mcp_servers",
    constraints: dict[str, Any] | None = None,
    run_local_probes: bool = False,
) -> dict[str, Any]:
    request = ObjectiveRouteRequest(
        query=query,
        objective=objective,
        data_scope=data_scope,  # type: ignore[arg-type]
        limit=limit,
        domain=domain,
        constraints=constraints or {},
    )
    payload = core_route_objective_with_probes(request, run_local_probes=run_local_probes, store=_store())
    payload.update(
        {
            "read_only": True,
            "local_metadata_probes_only": True,
            "live_mcp_call": False,
            "external_tool_execution": False,
            "security_certification": False,
            "action_authorization": False,
            "token_printed": False,
        }
    )
    return payload
