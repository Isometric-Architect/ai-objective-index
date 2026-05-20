from __future__ import annotations

from typing import Any

from .objective_router import (
    explain_route_decision as core_explain_route_decision,
    get_capability_trust as core_get_capability_trust,
    route_objective as core_route_objective,
)
from .objective_router_models import ObjectiveRouteRequest


def route_objective(
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
    payload = core_route_objective(request).model_dump(mode="json", by_alias=True)
    payload.update(
        {
            "read_only": True,
            "no_network": True,
            "probe_execution": False,
            "external_tool_execution": False,
            "forbidden_actions_exposed": False,
        }
    )
    return payload


def get_capability_trust(capability_id: str, data_scope: str = "sample") -> dict[str, Any]:
    payload = core_get_capability_trust(capability_id=capability_id, data_scope=data_scope)
    payload.update(
        {
            "read_only": True,
            "no_network": True,
            "probe_execution": False,
            "external_tool_execution": False,
        }
    )
    return payload


def explain_route_decision(
    capability_id: str,
    objective: str | None = None,
    data_scope: str = "sample",
) -> dict[str, Any]:
    payload = core_explain_route_decision(
        capability_id=capability_id,
        objective=objective,
        data_scope=data_scope,
    )
    payload.update(
        {
            "read_only": True,
            "no_network": True,
            "probe_execution": False,
            "external_tool_execution": False,
        }
    )
    return payload
