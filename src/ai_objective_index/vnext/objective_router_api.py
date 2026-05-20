from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .objective_router import get_capability_trust, route_objective, router_status
from .objective_router_models import ObjectiveRouteRequest


router = APIRouter(tags=["vnext-objective-router"])


@router.post("/v1/objectives/route")
def post_objective_route(request: ObjectiveRouteRequest) -> dict:
    return route_objective(request).model_dump(mode="json", by_alias=True)


@router.post("/v1/objectives/trust-report")
def post_objective_trust_report(request: ObjectiveRouteRequest) -> dict:
    return route_objective(request).model_dump(mode="json", by_alias=True)


@router.get("/v1/capabilities/{capability_id}/trust")
def get_capability_trust_endpoint(
    capability_id: str,
    data_scope: str = Query(default="sample"),
    objective: str | None = None,
    query: str | None = None,
):
    result = get_capability_trust(
        capability_id=capability_id,
        data_scope=data_scope,
        query=query,
        objective=objective,
    )
    if result.get("found") is False:
        return JSONResponse(status_code=404, content=result)
    return result


@router.get("/v1/objectives/router/status")
def get_objective_router_status() -> dict:
    return router_status()
