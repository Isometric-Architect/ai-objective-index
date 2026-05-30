from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from . import timestamp, write_json
from .agent_claim_boundary import CLAIM_BOUNDARY, MUST_NOT_CLAIM
from .agent_staleness_policy import freshness_for_sample
from .cdp_rest_adapters import attach_discover_cdp


DISCOVER_REQUEST_PATH = Path("api") / "vnext" / "examples" / "agent" / "discover_request.json"
DISCOVER_RESPONSE_PATH = Path("api") / "vnext" / "examples" / "agent" / "discover_response.json"


def sample_discover_request() -> dict[str, Any]:
    return {
        "schema": "AOI_AgentDiscoverRequest/v0.1",
        "objective": "Find source-traced MCP/tool/API candidates for selecting a read-only capability discovery helper.",
        "query": "AI capability discovery MCP tool with source traces and pre-use trust routing",
        "data_scope": "sample",
        "desired_capability_type": "mcp_or_api",
        "freshness_preference": "prefer_recent_source_traces_but_keep_hold_candidates_visible",
    }


def _sample_candidates() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "aoi-read-only-mcp-tools",
            "name": "AI Objective Index read-only MCP tools",
            "capability_type": "mcp_server",
            "why_relevant": "Matches objective-to-capability discovery and returns source traces, missing fields, and decision receipts.",
            "source_trace_refs": ["README.md#mcp-usage", "docs/mcp_usage.md#tool-set"],
            "missing_fields": ["live_registry_listing_status", "operator_permission_scope", "recent_source_refresh"],
            "preliminary_route_decision": "HOLD_MISSING_PERMISSION_SCOPE",
            "next_action": "Run preflight before any recommendation or tool use; keep output read-only until permission scope is explicit.",
            "must_not_claim": MUST_NOT_CLAIM,
            "residualops_escalation": "AgentSec",
        },
        {
            "candidate_id": "agentsec-local-manifest-review",
            "name": "AgentSec local manifest review",
            "capability_type": "local_receipt_workflow",
            "why_relevant": "Useful when the candidate is a tool or MCP manifest and an agent needs permission or hidden-instruction review.",
            "source_trace_refs": ["docs/agentsec_manifest_scanner.md", "pilot_receipts/agentsec/"],
            "missing_fields": ["owner_supplied_manifest", "redacted_permission_scope"],
            "preliminary_route_decision": "HOLD_POLICY_CLARITY",
            "next_action": "Request an owner-provided local manifest and run only local/offline review.",
            "must_not_claim": MUST_NOT_CLAIM,
            "residualops_escalation": "AgentSec",
        },
        {
            "candidate_id": "datacapsule-manifest-review",
            "name": "DataCapsule local corpus manifest review",
            "capability_type": "data_use_boundary_review",
            "why_relevant": "Useful when the objective depends on dataset, corpus, privacy, rights, or eval-leakage boundaries.",
            "source_trace_refs": ["docs/datacapsule_use_rights.md", "pilot_receipts/datacapsule/"],
            "missing_fields": ["source_rights_summary", "privacy_declared_status", "eval_overlap_status"],
            "preliminary_route_decision": "HOLD_POLICY_CLARITY",
            "next_action": "Ask for a local corpus manifest; do not inspect raw private data or authorize training/action use.",
            "must_not_claim": MUST_NOT_CLAIM,
            "residualops_escalation": "DataCapsule",
        },
    ]


def discover_capabilities(request: dict[str, Any] | None = None) -> dict[str, Any]:
    request = request or sample_discover_request()
    candidates = _sample_candidates()
    allow_candidates = [item for item in candidates if str(item["preliminary_route_decision"]).startswith("ALLOW")]
    best_current = allow_candidates[0] if allow_candidates else candidates[0]
    response = {
        "schema": "AOI_AgentDiscoverResponse/v0.1",
        "generated_at": timestamp(),
        "objective": request.get("objective", ""),
        "mode": "discover",
        "query": request.get("query", ""),
        "data_scope": request.get("data_scope", "sample"),
        "ranking_method": "transparent_public_demo_relevance_fields_only",
        "private_kernel_exposed": False,
        "candidates": candidates,
        "top_candidates": candidates,
        "best_current_candidate": best_current,
        "source_traces": sorted({trace for candidate in candidates for trace in candidate["source_trace_refs"]}),
        "route_decision": "HOLD_WITH_ACTIONABLE_NEXT_STEPS",
        "reason": "All current sample candidates are useful but remain HOLD until preflight resolves permissions, freshness, and policy clarity.",
        "missing_fields": sorted({field for candidate in candidates for field in candidate["missing_fields"]}),
        "next_action": "Choose the most relevant HOLD candidate, run preflight, and request missing fields instead of executing or over-recommending.",
        "must_not_claim": MUST_NOT_CLAIM,
        "claim_boundary": CLAIM_BOUNDARY,
        "residualops_escalation": {
            "tool_manifest_risk": "AgentSec",
            "code_or_release_risk": "QIRA",
            "data_or_use_boundary_risk": "DataCapsule",
            "enterprise_receipt_tracking": "ResidualOps dashboard",
        },
        "freshness": freshness_for_sample(needs_refresh=True),
        "external_action_performed": False,
        "live_network_used": False,
    }
    return attach_discover_cdp(response)


def write_sample_discover_examples() -> dict[str, Any]:
    request = sample_discover_request()
    response = discover_capabilities(request)
    write_json(DISCOVER_REQUEST_PATH, request)
    write_json(DISCOVER_RESPONSE_PATH, response)
    return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Write sample request/response.")
    args = parser.parse_args()
    response = write_sample_discover_examples() if args.sample else discover_capabilities()
    print(f"discover_mode: {response['route_decision']} candidates={len(response['top_candidates'])}")


if __name__ == "__main__":
    main()
