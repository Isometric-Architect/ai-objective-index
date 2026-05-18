from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from .action_boundary import forbidden_actions_v0_1
from . import mcp_tools
from .api_models import (
    CompareRequest,
    DecisionReceiptRequest,
    RankOptionsRequest,
    SearchResponse,
)
from .curated_loader import load_curated_source_traces
from .generated_loader import load_generated_objects, load_generated_source_traces
from .integrated_store import get_store_for_scope
from .registry_intake.mcp_registry_loader import load_registry_source_traces
from .seed_loader import load_sample_index, load_source_traces
from .store import ObjectiveIndexStore


DATA_SCOPE_PATTERN = "^(sample|generated|integrated|curated|public_beta|mcp_registry|public_beta_mcp)$"

app = FastAPI(
    title="AI Objective Index",
    version="0.1",
    description="Read-only objective-fit ranking API for local AOI sample records.",
)


def _store(data_scope: str = "sample") -> ObjectiveIndexStore:
    if data_scope == "sample":
        return ObjectiveIndexStore(load_sample_index(), load_source_traces())
    return get_store_for_scope(data_scope)


def _object_not_found(object_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": "object_not_found",
            "object_id": object_id,
            "message": "No object found for object_id.",
        },
    )


def _object_exists(object_id: str, data_scope: str = "sample") -> bool:
    return _store(data_scope).get_object(object_id) is not None


def _generated_counts() -> dict[str, int]:
    try:
        return {
            "generated_object_count": len(load_generated_objects()),
            "generated_source_trace_count": len(load_generated_source_traces()),
        }
    except Exception:
        return {"generated_object_count": 0, "generated_source_trace_count": 0}


def _curated_counts() -> dict[str, int]:
    try:
        curated_store = get_store_for_scope("curated")
        public_beta_store = get_store_for_scope("public_beta")
        public_beta_trace_count = sum(
            len(public_beta_store.get_traces(item.object_id))
            for item in public_beta_store.list_objects()
        )
        return {
            "curated_object_count": len(curated_store.list_objects()),
            "curated_source_trace_count": len(load_curated_source_traces()),
            "public_beta_object_count": len(public_beta_store.list_objects()),
            "public_beta_source_trace_count": public_beta_trace_count,
        }
    except Exception:
        return {
            "curated_object_count": 0,
            "curated_source_trace_count": 0,
            "public_beta_object_count": 0,
            "public_beta_source_trace_count": 0,
        }


def _mcp_registry_counts() -> dict[str, int]:
    try:
        registry_store = get_store_for_scope("mcp_registry")
        public_beta_mcp_store = get_store_for_scope("public_beta_mcp")
        public_beta_trace_count = sum(
            len(public_beta_mcp_store.get_traces(item.object_id))
            for item in public_beta_mcp_store.list_objects()
        )
        return {
            "mcp_registry_object_count": len(registry_store.list_objects()),
            "mcp_registry_source_trace_count": len(load_registry_source_traces()),
            "public_beta_mcp_object_count": len(public_beta_mcp_store.list_objects()),
            "public_beta_mcp_source_trace_count": public_beta_trace_count,
            "public_beta_mcp_definition": "registry_metadata_candidate_not_verified",
        }
    except Exception:
        return {
            "mcp_registry_object_count": 0,
            "mcp_registry_source_trace_count": 0,
            "public_beta_mcp_object_count": 0,
            "public_beta_mcp_source_trace_count": 0,
            "public_beta_mcp_definition": "registry_metadata_candidate_not_verified",
        }


@app.get("/status")
def status() -> dict[str, Any]:
    objects = load_sample_index()
    traces = load_source_traces()
    generated = _generated_counts()
    curated = _curated_counts()
    registry = _mcp_registry_counts()
    return {
        "service": "ai-objective-index",
        "version": "0.1",
        "read_only": True,
        "default_data_scope": "sample",
        "live_network_enabled": False,
        "productization_mode": True,
        "product_claims_require_evidence": True,
        "sample_object_count": len(objects),
        "sample_source_trace_count": len(traces),
        "object_count": len(objects),
        "source_trace_count": len(traces),
        **generated,
        **curated,
        **registry,
        "integrated_object_count": len(objects) + generated["generated_object_count"],
        "integrated_source_trace_count": len(traces) + generated["generated_source_trace_count"],
        "forbidden_actions": mcp_tools.FORBIDDEN_ACTIONS,
        "action_boundary": {
            "read_only_allowed": [
                "READ",
                "RANK",
                "COMPARE",
                "EXPLAIN",
                "QUOTE_SNIPPET",
                "DECISION_RECEIPT",
            ],
            "blocked_actions": forbidden_actions_v0_1(),
        },
    }


@app.get("/search", response_model=SearchResponse)
def search(
    query: str,
    domain: str | None = None,
    objective: str | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    data_scope: str = Query(default="sample", pattern=DATA_SCOPE_PATTERN),
) -> dict[str, Any]:
    result = mcp_tools.search_objectives(
        query=query,
        domain=domain,
        objective=objective,
        limit=limit,
        data_scope=data_scope,
    )
    return {
        "read_only": True,
        "data_scope": data_scope,
        "query": result["query"],
        "objective": objective,
        "results": result["results"],
        "limitations": result["known_limits"],
        "warnings": result.get("warnings", []),
        "forbidden_actions": result["forbidden_actions"],
        "action_boundary": result.get("action_boundary", {}),
    }


@app.get("/objects/{object_id}", response_model=None)
def get_object(object_id: str, data_scope: str = Query(default="sample", pattern=DATA_SCOPE_PATTERN)):
    action_object = _store(data_scope).get_object(object_id)
    if action_object is None:
        return _object_not_found(object_id)
    return action_object.model_dump(mode="json")


@app.post("/rank")
def rank(request: RankOptionsRequest) -> dict[str, Any]:
    return mcp_tools.rank_options(
        options=[option.model_dump(mode="json") for option in request.options],
        objective=request.objective,
        constraints=request.constraints,
        scoring_profile=request.scoring_profile,
        data_scope=request.data_scope,
    )


@app.post("/compare")
def compare(request: CompareRequest) -> dict[str, Any]:
    return mcp_tools.compare_tools(
        tool_ids=request.object_ids,
        compare_fields=request.compare_fields,
        query=request.query,
        objective=request.objective,
        constraints=request.constraints,
        data_scope=request.data_scope,
    )


@app.get("/objects/{object_id}/score", response_model=None)
def score(object_id: str, data_scope: str = Query(default="sample", pattern=DATA_SCOPE_PATTERN)):
    if not _object_exists(object_id, data_scope=data_scope):
        return _object_not_found(object_id)
    return mcp_tools.explain_score(object_id, data_scope=data_scope)


@app.get("/objects/{object_id}/source-trace", response_model=None)
def source_trace(
    object_id: str,
    field: str | None = None,
    data_scope: str = Query(default="sample", pattern=DATA_SCOPE_PATTERN),
):
    if not _object_exists(object_id, data_scope=data_scope):
        return _object_not_found(object_id)
    return mcp_tools.get_source_trace(object_id, field=field, data_scope=data_scope)


@app.get("/objects/{object_id}/missing-fields", response_model=None)
def missing_fields(object_id: str, data_scope: str = Query(default="sample", pattern=DATA_SCOPE_PATTERN)):
    if not _object_exists(object_id, data_scope=data_scope):
        return _object_not_found(object_id)
    return mcp_tools.list_missing_fields(object_id, data_scope=data_scope)


@app.post("/decision-receipt", response_model=None)
def decision_receipt(request: DecisionReceiptRequest):
    if not _object_exists(request.selected_object_id, data_scope=request.data_scope):
        return _object_not_found(request.selected_object_id)
    return mcp_tools.generate_decision_receipt(
        query=request.query,
        selected_object_id=request.selected_object_id,
        alternatives=request.alternatives,
        objective=request.objective,
        constraints=request.constraints,
        data_scope=request.data_scope,
    )


def main() -> None:
    try:
        import uvicorn
    except Exception:
        print("Install uvicorn to run the API server, or use TestClient/tests.")
        return
    uvicorn.run("ai_objective_index.api:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
