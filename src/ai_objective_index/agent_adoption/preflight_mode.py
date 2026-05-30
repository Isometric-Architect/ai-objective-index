from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from . import timestamp, write_json
from .agent_claim_boundary import CLAIM_BOUNDARY, MUST_NOT_CLAIM
from .agent_staleness_policy import freshness_for_sample
from .cdp_rest_adapters import attach_preflight_cdp


PREFLIGHT_REQUEST_PATH = Path("api") / "vnext" / "examples" / "agent" / "preflight_request.json"
PREFLIGHT_RESPONSE_PATH = Path("api") / "vnext" / "examples" / "agent" / "preflight_response.json"

SECRET_PATTERN = re.compile(r"\b(sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9_]{12,}|hf_[A-Za-z0-9]{12,}|PRIVATE KEY|api_key\s*=)", re.I)
EXTERNAL_ACTION_TERMS = [
    "execute",
    "call github api",
    "create issue",
    "comment on pr",
    "merge",
    "deploy",
    "publish",
    "upload",
    "train model",
    "live mcp call",
    "external action",
]
CERTIFICATION_TERMS = [
    "security certified",
    "certified safe",
    "code correctness proven",
    "production ready",
    "production-ready",
    "quality guaranteed",
    "legal compliance",
    "privacy compliant",
    "license cleared",
]


def sample_preflight_request() -> dict[str, Any]:
    return {
        "schema": "AOI_AgentPreflightRequest/v0.1",
        "candidate_id": "aoi-read-only-mcp-tools",
        "intended_use": "Use the candidate for read-only comparison and produce a recommendation only after permission scope is clear.",
        "available_metadata": {
            "source_trace_refs": ["README.md#mcp-usage", "docs/mcp_usage.md#tool-set"],
            "tool_available": True,
            "permission_scope": "",
            "privacy_policy": "",
            "data_retention": "",
            "last_checked_at": "2026-05-30T00:00:00Z",
        },
        "required_permissions": ["read-only metadata review"],
        "organization_policy_optional": {},
    }


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def preflight_capability(request: dict[str, Any] | None = None) -> dict[str, Any]:
    request = request or sample_preflight_request()
    metadata = request.get("available_metadata", {}) if isinstance(request.get("available_metadata"), dict) else {}
    text = " ".join(
        [
            str(request.get("intended_use", "")),
            " ".join(str(item) for item in request.get("required_permissions", [])),
            " ".join(f"{key}={value}" for key, value in metadata.items()),
        ]
    )
    missing_fields: list[str] = []
    if not metadata.get("permission_scope"):
        missing_fields.append("permission_scope")
    if not metadata.get("privacy_policy"):
        missing_fields.append("privacy_policy")
    if not metadata.get("data_retention"):
        missing_fields.append("data_retention")

    if SECRET_PATTERN.search(text):
        decision = "BLOCK_SECRET_OR_PRIVATE_DATA"
        reason = "The request or metadata appears to include a token, credential, private key, or secret-like value."
        residualops = "ResidualOps manual review"
    elif _contains_any(text, CERTIFICATION_TERMS):
        decision = "BLOCK_CERTIFICATION_CLAIM"
        reason = "The intended use asks AOI to support a certification, proof, compliance, quality, or product-readiness claim."
        residualops = "ResidualOps dashboard"
    elif _contains_any(text, EXTERNAL_ACTION_TERMS):
        decision = "BLOCK_EXTERNAL_ACTION"
        reason = "The intended use asks for live execution or external mutation; tool availability is not tool authorization."
        residualops = "AgentSec"
    elif "permission_scope" in missing_fields:
        decision = "HOLD_MISSING_PERMISSION_SCOPE"
        reason = "The candidate may be useful, but the permission scope is missing; availability alone does not authorize use."
        residualops = "AgentSec"
    elif missing_fields:
        decision = "HOLD_POLICY_CLARITY"
        reason = "The candidate lacks policy, privacy, or data-retention clarity needed before recommendation or use."
        residualops = "AgentSec"
    elif metadata.get("needs_refresh") is True:
        decision = "HOLD_STALE_METADATA"
        reason = "The available source traces need refresh before external-facing recommendation."
        residualops = "ResidualOps dashboard"
    else:
        decision = "ALLOW_READ_ONLY_REVIEW"
        reason = "The request is limited to read-only review and does not ask for external action or unsupported claims."
        residualops = "ResidualOps dashboard"

    response = {
        "schema": "AOI_AgentPreflightResponse/v0.1",
        "generated_at": timestamp(),
        "objective": request.get("intended_use", ""),
        "mode": "preflight",
        "candidate_id": request.get("candidate_id", ""),
        "route_decision": decision,
        "reason": reason,
        "missing_fields": missing_fields,
        "next_action": _next_action_for_decision(decision),
        "allowed_next_steps": [
            "read local metadata",
            "compare candidates with missing fields visible",
            "request missing permission or policy details",
            "escalate to ResidualOps local receipt workflow",
        ],
        "forbidden_next_steps": [
            "external tool execution",
            "GitHub API call",
            "issue or PR comment creation",
            "merge, deploy, publish, upload, or train",
            "credential use",
            "certification or product-readiness claim",
        ],
        "must_not_claim": MUST_NOT_CLAIM,
        "claim_ceiling": CLAIM_BOUNDARY,
        "residualops_escalation": residualops,
        "freshness": freshness_for_sample(needs_refresh=metadata.get("needs_refresh", True) is True),
        "tool_available_is_tool_authorized": False,
        "external_action_performed": False,
        "live_network_used": False,
    }
    return attach_preflight_cdp(response)


def _next_action_for_decision(decision: str) -> str:
    return {
        "ALLOW_READ_ONLY_REVIEW": "Proceed with read-only comparison only; do not execute external actions.",
        "HOLD_MISSING_PERMISSION_SCOPE": "Ask for permission scope or manifest metadata, then rerun preflight.",
        "HOLD_POLICY_CLARITY": "Request missing policy, privacy, retention, or pricing fields before recommendation.",
        "HOLD_STALE_METADATA": "Refresh source traces before external-facing recommendation.",
        "BLOCK_EXTERNAL_ACTION": "Stop execution path and convert the task into a local review or owner-consented workflow.",
        "BLOCK_CERTIFICATION_CLAIM": "Remove certification/proof/readiness wording and restate as a bounded route decision.",
        "BLOCK_SECRET_OR_PRIVATE_DATA": "Remove secrets/private data and rerun redaction before any review.",
    }.get(decision, "Hold for manual triage.")


def write_sample_preflight_examples() -> dict[str, Any]:
    request = sample_preflight_request()
    response = preflight_capability(request)
    write_json(PREFLIGHT_REQUEST_PATH, request)
    write_json(PREFLIGHT_RESPONSE_PATH, response)
    return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Write sample request/response.")
    args = parser.parse_args()
    response = write_sample_preflight_examples() if args.sample else preflight_capability()
    print(f"preflight_mode: {response['route_decision']} missing={len(response['missing_fields'])}")


if __name__ == "__main__":
    main()
