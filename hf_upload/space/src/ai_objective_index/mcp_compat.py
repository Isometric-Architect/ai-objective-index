from __future__ import annotations

import json
from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from . import mcp_tools
from .integrated_store import get_store_for_scope


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return value


def _assert_jsonable(payload: dict[str, Any]) -> dict[str, Any]:
    value = _jsonable(payload)
    json.dumps(value)
    return value


def search(query: str, data_scope: str = "sample", limit: int = 10) -> dict[str, Any]:
    """Generic read-only MCP search wrapper.

    It adapts AOI objective search to MCP clients that expect a simple
    `search` tool. It never crawls or fetches network resources.
    """

    result = mcp_tools.search_objectives(
        query=query,
        data_scope=data_scope,
        limit=limit,
    )
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": result.get("data_scope", data_scope),
            "query": query,
            "results": result.get("results", []),
            "status": "ok",
            "confidence": result["results"][0].get("confidence") if result.get("results") else None,
            "source_urls": [
                url
                for row in result.get("results", [])
                for url in row.get("source_urls", [])
            ][:20],
            "limitations": result.get("known_limits", []),
            "forbidden_actions": result.get("forbidden_actions", mcp_tools.FORBIDDEN_ACTIONS),
            "known_limits": result.get("known_limits", []),
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
        }
    )


def fetch(object_id: str, data_scope: str = "sample") -> dict[str, Any]:
    """Generic read-only MCP fetch wrapper for one local AOI object."""

    store = get_store_for_scope(data_scope)
    action_object = store.get_object(object_id)
    if action_object is None:
        return _assert_jsonable(
            {
                "read_only": True,
                "data_scope": data_scope,
                "object_id": object_id,
                "status": "not_found",
                "confidence": None,
                "error": "object_not_found",
                "message": "No object found for object_id in the selected local AOI data scope.",
                "limitations": mcp_tools.KNOWN_LIMITS,
                "known_limits": mcp_tools.KNOWN_LIMITS,
                "forbidden_actions": mcp_tools.FORBIDDEN_ACTIONS,
                "not_verified": data_scope == "public_beta_mcp",
                "not_security_certified": data_scope == "public_beta_mcp",
                "not_quality_guarantee": True,
            }
        )

    score = mcp_tools.explain_score(object_id, data_scope=data_scope)
    traces = mcp_tools.get_source_trace(object_id, data_scope=data_scope)
    missing = mcp_tools.list_missing_fields(object_id, data_scope=data_scope)
    object_payload = action_object.model_dump(mode="json")
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            "object_id": object_id,
            "status": object_payload.get("status"),
            "confidence": object_payload.get("confidence"),
            "object": object_payload,
            "score": score,
            "source_traces": traces.get("traces", []),
            "source_trace": traces.get("traces", []),
            "source_urls": object_payload.get("source_urls", []),
            "missing_fields": missing.get("missing_fields", []),
            "limitations": mcp_tools.KNOWN_LIMITS,
            "known_limits": mcp_tools.KNOWN_LIMITS,
            "forbidden_actions": mcp_tools.FORBIDDEN_ACTIONS,
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
        }
    )
