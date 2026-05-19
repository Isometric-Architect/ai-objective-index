from __future__ import annotations

import json
from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from .action_boundary import check_action_boundary, forbidden_actions_v0_1
from .compare import compare_objects
from .decision_receipt import generate_decision_receipt as core_generate_decision_receipt
from .integrated_store import get_store_for_scope
from .models import ActionObject
from .scoring import score_object
from .seed_loader import load_sample_index, load_source_traces
from .source_trace import get_source_trace as core_get_source_trace
from .store import ObjectiveIndexStore
from .use_rights import default_use_rights_for_object


FORBIDDEN_ACTIONS = [
    "payment",
    "booking",
    "login",
    "email_sending",
    "form_submission",
    "purchase",
    "contract_signing",
    "account_connection",
]

KNOWN_LIMITS = [
    "v0.1 read-only benchmark output",
    "not a quality guarantee",
    "verify source traces before production use",
    "no purchase, booking, payment, login, email, or contract execution",
]

REGISTRY_NOT_ASSERTED = [
    "not supplier verified",
    "not security certified",
    "not a quality guarantee",
    "not action permission",
    "not purchasing advice",
]

_SCORING_PROFILES: dict[str, dict[str, dict[str, float]]] = {
    "default": {
        "weights": {
            "relevance": 0.2,
            "cost_fit": 0.12,
            "policy_clarity": 0.12,
            "documentation_quality": 0.12,
            "trust_signal": 0.1,
            "source_trace_coverage": 0.12,
            "freshness": 0.08,
            "capability_fit": 0.1,
            "structuredness": 0.04,
        }
    },
    "cost_sensitive": {
        "weights": {
            "relevance": 0.16,
            "cost_fit": 0.28,
            "policy_clarity": 0.1,
            "documentation_quality": 0.1,
            "trust_signal": 0.08,
            "source_trace_coverage": 0.1,
            "freshness": 0.06,
            "capability_fit": 0.08,
            "structuredness": 0.04,
        }
    },
    "privacy_sensitive": {
        "weights": {
            "relevance": 0.16,
            "cost_fit": 0.08,
            "policy_clarity": 0.26,
            "documentation_quality": 0.1,
            "trust_signal": 0.12,
            "source_trace_coverage": 0.14,
            "freshness": 0.06,
            "capability_fit": 0.04,
            "structuredness": 0.04,
        }
    },
    "developer_friendly": {
        "weights": {
            "relevance": 0.16,
            "cost_fit": 0.08,
            "policy_clarity": 0.08,
            "documentation_quality": 0.26,
            "trust_signal": 0.1,
            "source_trace_coverage": 0.1,
            "freshness": 0.06,
            "capability_fit": 0.12,
            "structuredness": 0.04,
        }
    },
    "commercial_use": {
        "weights": {
            "relevance": 0.18,
            "cost_fit": 0.12,
            "policy_clarity": 0.24,
            "documentation_quality": 0.1,
            "trust_signal": 0.1,
            "source_trace_coverage": 0.12,
            "freshness": 0.06,
            "capability_fit": 0.04,
            "structuredness": 0.04,
        }
    },
}


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


def _assert_jsonable(value: Any) -> dict[str, Any]:
    payload = _jsonable(value)
    json.dumps(payload)
    return payload


def _load_store(data_scope: str = "sample") -> ObjectiveIndexStore:
    if data_scope == "sample":
        return ObjectiveIndexStore(load_sample_index(), load_source_traces())
    return get_store_for_scope(data_scope)


def _normalize_domain(domain: str | None) -> str | None:
    if domain is None:
        return None
    return {
        "apis": "ai_apis",
        "api": "ai_apis",
        "saas": "ai_saas",
        "tools": "ai_tools",
        "tool": "ai_tools",
        "mcp": "mcp_servers",
        "mcp_servers": "mcp_servers",
        "services": "mixed_ai_tools",
        "datasets": "mixed_ai_tools",
    }.get(domain.lower(), domain)


def _normalize_constraints(constraints: dict[str, Any] | None) -> dict[str, Any]:
    normalized = dict(constraints or {})
    if "budget_max" in normalized and "max_monthly_budget_usd" not in normalized:
        normalized["max_monthly_budget_usd"] = normalized["budget_max"]
    if normalized.get("commercial_use_required"):
        normalized["requires_documented_terms"] = True
    return normalized


def _score_profile(scoring_profile: str | dict[str, Any] = "default") -> str | dict[str, Any]:
    if isinstance(scoring_profile, str):
        return _SCORING_PROFILES.get(scoring_profile, _SCORING_PROFILES["default"])
    return scoring_profile


def _result_from_object(
    action_object: ActionObject,
    store: ObjectiveIndexStore,
    query: str | None = None,
    objective: Any = None,
    constraints: dict[str, Any] | None = None,
    scoring_profile: str | dict[str, Any] = "default",
) -> dict[str, Any]:
    traces = store.get_traces(action_object.object_id)
    score = score_object(
        action_object,
        query=query,
        objective=objective,
        constraints=_normalize_constraints(constraints),
        traces=traces,
        scoring_profile=_score_profile(scoring_profile),
    )
    return {
        "object_id": action_object.object_id,
        "name": action_object.name,
        "object_type": action_object.object_type,
        "summary": action_object.summary,
        "objective_score": score.objective_score,
        "confidence": score.confidence,
        "status": score.status,
        "rank_reason": score.rank_reason,
        "missing_fields": score.missing_fields,
        "source_urls": action_object.source_urls,
        "source_trace_ids": [trace.trace_id for trace in traces],
        "warnings": score.warnings,
        "claim_ceiling": score.claim_ceiling,
        "not_asserted": score.not_asserted,
        "obstructions": score.obstructions,
        "use_rights": default_use_rights_for_object(action_object),
        "display_status": getattr(action_object, "display_status", None)
        or (
            "REGISTRY_METADATA_CANDIDATE"
            if bool(getattr(action_object, "beta_candidate", False))
            else None
        ),
        "not_verified": True,
        "not_security_certified": True,
        "not_quality_guarantee": True,
    }


def search_objectives(
    query: str,
    domain: str | None = None,
    objective: str | None = None,
    constraints: dict[str, Any] | None = None,
    limit: int = 10,
    data_scope: str = "sample",
) -> dict[str, Any]:
    store = _load_store(data_scope)
    candidates = store.search_objects(query, domain=_normalize_domain(domain), limit=max(limit, 1))
    results = [
        _result_from_object(
            candidate,
            store,
            query=query,
            objective=objective,
            constraints=constraints,
        )
        for candidate in candidates
    ]
    results.sort(key=lambda item: item["objective_score"], reverse=True)
    warnings: list[str] = []
    if data_scope == "public_beta" and not results:
        warnings.append(
            "No public_beta curated objects available yet; add manually curated source-traced rows first."
        )
    if data_scope == "curated" and not results:
        warnings.append("No curated objects available for this query in the local curated dataset.")
    if data_scope == "public_beta_mcp" and not results:
        warnings.append(
            "No public_beta_mcp candidates available; run registry_beta_dataset_builder after real or manual Official MCP Registry metadata is present."
        )
    if data_scope == "mcp_registry" and not results:
        warnings.append("No MCP registry objects available; run the offline registry fixture export first.")
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            "query": query,
            "domain": domain,
            "results": results[:limit],
            "warnings": warnings,
            "known_limits": KNOWN_LIMITS,
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
            "not_asserted": REGISTRY_NOT_ASSERTED if data_scope == "public_beta_mcp" else ["not a quality guarantee"],
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "action_boundary": {
                "read": check_action_boundary("READ"),
                "rank": check_action_boundary("RANK"),
                "blocked_actions": forbidden_actions_v0_1(),
            },
        }
    )


def rank_options(
    options: list[dict[str, Any]],
    objective: str,
    constraints: dict[str, Any] | None = None,
    scoring_profile: str = "default",
    data_scope: str = "sample",
) -> dict[str, Any]:
    store = _load_store(data_scope)
    objects_by_name = {item.name.lower(): item for item in store.list_objects()}
    ranked: list[dict[str, Any]] = []

    for option in options:
        name = str(option.get("name", "")).strip()
        action_object = objects_by_name.get(name.lower())
        if action_object is None:
            ranked.append(
                {
                    "name": name,
                    "url": option.get("url"),
                    "description": option.get("description"),
                    "objective_score": 10.0,
                    "confidence": 0.1,
                    "status": "UNVERIFIED",
                    "rank_reason": [
                        "Option is not in the local sample index; score is incomplete."
                    ],
                    "missing_fields": [
                        "pricing",
                        "source_traces",
                        "policies",
                        "docs",
                    ],
                    "warnings": [
                        "Option is not in the local sample index; score is incomplete.",
                        "No network calls or URL crawling were performed.",
                    ],
                    "claim_ceiling": "EXTRACTED_UNVERIFIED",
                    "not_asserted": [
                        "not a quality guarantee",
                        "not permission to buy, book, pay, log in, submit forms, email, connect accounts, purchase, or sign contracts",
                    ],
                    "use_rights": {
                        "READ": {"decision": "ALLOW"},
                        "RANK": {"decision": "ALLOW"},
                        "COMPARE": {"decision": "ALLOW"},
                        "QUOTE": {"decision": "ALLOW"},
                        "TRAIN": {"decision": "BLOCK"},
                        "SHARE": {"decision": "BLOCK"},
                        "MEMORY": {"decision": "HOLD"},
                        "ACTION": {"decision": "BLOCK"},
                    },
                }
            )
            continue
        ranked.append(
            _result_from_object(
                action_object,
                store,
                query=objective,
                objective=objective,
                constraints=constraints,
                scoring_profile=scoring_profile,
            )
        )

    ranked.sort(key=lambda item: item["objective_score"], reverse=True)
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            "objective": objective,
            "scoring_profile": scoring_profile,
            "results": ranked,
            "known_limits": KNOWN_LIMITS,
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
            "action_boundary": {
                "rank": check_action_boundary("RANK"),
                "blocked_actions": forbidden_actions_v0_1(),
            },
        }
    )


def compare_tools(
    tool_ids: list[str],
    compare_fields: list[str] | None = None,
    query: str | None = None,
    objective: str | None = None,
    constraints: dict[str, Any] | None = None,
    data_scope: str = "sample",
) -> dict[str, Any]:
    store = _load_store(data_scope)
    result = compare_objects(
        store,
        tool_ids,
        compare_fields=compare_fields,
        query=query or objective,
        objective=objective,
        constraints=_normalize_constraints(constraints),
    )
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            **result.model_dump(mode="json"),
            "known_limits": KNOWN_LIMITS,
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
            "action_boundary": {
                "compare": check_action_boundary("COMPARE"),
                "blocked_actions": forbidden_actions_v0_1(),
            },
        }
    )


def explain_score(object_id: str, data_scope: str = "sample") -> dict[str, Any]:
    store = _load_store(data_scope)
    action_object = store.get_object(object_id)
    if action_object is None:
        return _assert_jsonable(
            {
                "read_only": True,
                "data_scope": data_scope,
                "object_id": object_id,
                "error": "Object not found in selected local AOI index.",
                "known_limits": KNOWN_LIMITS,
            }
        )
    traces = store.get_traces(object_id)
    score = score_object(action_object, traces=traces)
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            **score.model_dump(mode="json"),
            "source_trace_ids": [trace.trace_id for trace in traces],
            "known_limits": KNOWN_LIMITS,
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "use_rights": default_use_rights_for_object(action_object),
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
            "action_boundary": {
                "explain": check_action_boundary("EXPLAIN"),
                "blocked_actions": forbidden_actions_v0_1(),
            },
        }
    )


def get_source_trace(object_id: str, field: str | None = None, data_scope: str = "sample") -> dict[str, Any]:
    store = _load_store(data_scope)
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            "object_id": object_id,
            "field": field,
            "traces": core_get_source_trace(store, object_id, field=field),
            "known_limits": [
                "source traces support fields but do not guarantee completeness or currentness"
            ],
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
            "action_boundary": {
                "quote_snippet": check_action_boundary("QUOTE_SNIPPET"),
                "blocked_actions": forbidden_actions_v0_1(),
            },
        }
    )


def list_missing_fields(object_id: str, data_scope: str = "sample") -> dict[str, Any]:
    store = _load_store(data_scope)
    missing = store.list_missing_fields(object_id)
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            "object_id": object_id,
            "missing_fields": [item.model_dump(mode="json") for item in missing],
            "known_limits": KNOWN_LIMITS,
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
            "action_boundary": {
                "read": check_action_boundary("READ"),
                "blocked_actions": forbidden_actions_v0_1(),
            },
        }
    )


def generate_decision_receipt(
    query: str,
    selected_object_id: str,
    alternatives: list[str] | None = None,
    objective: str | None = None,
    constraints: dict[str, Any] | None = None,
    data_scope: str = "sample",
) -> dict[str, Any]:
    store = _load_store(data_scope)
    receipt = core_generate_decision_receipt(
        store,
        selected_object_id=selected_object_id,
        alternatives=alternatives,
        query=query,
        objective=objective,
        constraints=_normalize_constraints(constraints),
    )
    payload = receipt.model_dump(mode="json")
    for known_limit in KNOWN_LIMITS:
        if known_limit not in payload["known_limits"]:
            payload["known_limits"].append(known_limit)
    return _assert_jsonable(
        {
            "read_only": True,
            "data_scope": data_scope,
            "decision_receipt": payload,
            "forbidden_actions": FORBIDDEN_ACTIONS,
            "not_verified": data_scope == "public_beta_mcp",
            "not_security_certified": data_scope == "public_beta_mcp",
            "not_quality_guarantee": True,
            "action_boundary": {
                "decision_receipt": check_action_boundary("DECISION_RECEIPT"),
                "blocked_actions": forbidden_actions_v0_1(),
            },
        }
    )
