from __future__ import annotations

from typing import Any

from ai_objective_index.agent_adoption.agent_claim_boundary import MUST_NOT_CLAIM
from ai_objective_index.agent_adoption.discover_mode import discover_capabilities, sample_discover_request
from ai_objective_index.agent_adoption.preflight_mode import preflight_capability, sample_preflight_request


def aoi_guided_result_for_case(case: dict[str, Any]) -> dict[str, Any]:
    discover = discover_capabilities(sample_discover_request())
    preflight = preflight_capability(sample_preflight_request())
    escalation = case.get("expected_residualops_escalation", "ResidualOps dashboard")
    candidates = discover["top_candidates"]
    return {
        "schema": "AOI_GuidedAgentEvalResult/v0.1",
        "case_id": case["case_id"],
        "objective": case["objective"],
        "mode": "discover_then_preflight",
        "top_candidates": candidates,
        "best_current_candidate": discover["best_current_candidate"],
        "source_traces": discover["source_traces"],
        "missing_fields": sorted(set(discover["missing_fields"] + preflight["missing_fields"])),
        "route_decision": preflight["route_decision"],
        "next_action": _next_action(case, preflight),
        "must_not_claim": MUST_NOT_CLAIM,
        "residualops_escalation": escalation,
        "freshness": discover["freshness"],
        "tool_available_is_tool_authorized": False,
        "hallucinated_candidate_accepted": False,
        "external_action_authorized": False,
        "certification_or_readiness_claimed": False,
        "notes": "AOI-guided fixture keeps useful candidates visible while preserving pre-use trust routing.",
    }


def _next_action(case: dict[str, Any], preflight: dict[str, Any]) -> str:
    case_id = str(case.get("case_id", ""))
    if "data" in case_id or "privacy" in case_id:
        return "Request a redacted local dataset or policy manifest and route use-boundary review to DataCapsule."
    if "code" in case_id or "release" in case_id:
        return "Request patch, CI, and release evidence locally and route release risk to QIRA."
    if "tool" in case_id or "permission" in case_id or "registry" in case_id:
        return "Request permission scope and manifest evidence, then route tool/manifest risk to AgentSec."
    if "hold_without_next_action" in case_id:
        return "Keep the best HOLD candidate visible and ask for missing permission, freshness, and policy fields."
    return str(preflight.get("next_action") or "Run preflight and request missing fields before use.")
