from __future__ import annotations

from pathlib import Path
from typing import Any

from . import read_text
from .capability_card import build_capability_card
from .discover_mode import discover_capabilities
from .preflight_mode import preflight_capability


def get_aoi_capability_card() -> dict[str, Any]:
    card = build_capability_card()
    return {
        "read_only": True,
        "external_api_used": False,
        "live_mcp_call_used": False,
        "action_authorization": False,
        "capability_card": card,
    }


def discover_capabilities_for_objective(
    objective: str,
    query: str,
    data_scope: str = "sample",
    desired_capability_type: str = "mcp_or_api",
    freshness_preference: str = "prefer_recent_source_traces_but_keep_hold_candidates_visible",
) -> dict[str, Any]:
    response = discover_capabilities(
        {
            "schema": "AOI_AgentDiscoverRequest/v0.1",
            "objective": objective,
            "query": query,
            "data_scope": data_scope,
            "desired_capability_type": desired_capability_type,
            "freshness_preference": freshness_preference,
        }
    )
    response.update(
        {
            "read_only": True,
            "external_api_used": False,
            "live_mcp_call_used": False,
            "action_authorization": False,
        }
    )
    return response


def preflight_capability_for_use(
    candidate_id: str,
    intended_use: str,
    available_metadata: dict[str, Any] | None = None,
    required_permissions: list[str] | None = None,
    organization_policy_optional: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = preflight_capability(
        {
            "schema": "AOI_AgentPreflightRequest/v0.1",
            "candidate_id": candidate_id,
            "intended_use": intended_use,
            "available_metadata": available_metadata or {},
            "required_permissions": required_permissions or [],
            "organization_policy_optional": organization_policy_optional or {},
        }
    )
    response.update(
        {
            "read_only": True,
            "external_api_used": False,
            "live_mcp_call_used": False,
            "action_authorization": False,
        }
    )
    return response


def explain_aoi_agent_use() -> dict[str, Any]:
    return {
        "read_only": True,
        "when_to_use": read_text(Path("agent_discovery") / "WHEN_TO_USE_AOI.md"),
        "when_not_to_use": read_text(Path("agent_discovery") / "WHEN_NOT_TO_USE_AOI.md"),
        "core_workflow": "Discover first. Preflight second. Claim boundary always.",
        "must_not_claim": build_capability_card()["claim_boundary"],
        "external_action_authorization": False,
        "external_api_used": False,
        "live_mcp_call_used": False,
    }


def list_aoi_agent_examples() -> dict[str, Any]:
    return {
        "read_only": True,
        "examples": [
            "agent_discovery/CAPABILITY_CARD.json",
            "agent_discovery/AGENT_DISCOVER_MODE.md",
            "agent_discovery/AGENT_PREFLIGHT_MODE.md",
            "api/vnext/examples/agent/discover_request.json",
            "api/vnext/examples/agent/discover_response.json",
            "api/vnext/examples/agent/preflight_request.json",
            "api/vnext/examples/agent/preflight_response.json",
            "examples/agent_prompts/discover_mcp_candidates.md",
            "examples/agent_prompts/preflight_mcp_candidate.md",
        ],
        "external_api_used": False,
        "live_mcp_call_used": False,
        "action_authorization": False,
    }
