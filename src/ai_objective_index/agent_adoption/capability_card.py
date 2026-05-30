from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from . import MCP_NAME, PACKAGE_NAME, VERSION, write_json, write_text
from .agent_claim_boundary import CLAIM_BOUNDARY


CAPABILITY_CARD_PATH = Path("agent_discovery") / "CAPABILITY_CARD.json"
CAPABILITY_CARD_MD_PATH = Path("agent_discovery") / "CAPABILITY_CARD.md"


def build_capability_card() -> dict[str, Any]:
    return {
        "schema": "AOI_CapabilityCard/v0.1",
        "name": "AI Objective Index",
        "package": PACKAGE_NAME,
        "version": VERSION,
        "mcp_name": MCP_NAME,
        "type": "objective_to_capability_discovery_and_preuse_trust_router",
        "primary_users": [
            "ordinary_ai_agent",
            "ai_app_builder",
            "mcp_client",
            "developer",
            "enterprise_governance_operator",
        ],
        "best_for": [
            "finding source-traced MCP/tool/API candidates for a specific objective",
            "returning useful top candidates with missing fields",
            "adding conservative pre-use route decisions",
            "explaining HOLD/BLOCK reasons",
            "producing must-not-claim boundaries",
            "escalating to ResidualOps gates when enterprise use is needed",
        ],
        "not_for": [
            "security certification",
            "provider verification",
            "automatic tool execution",
            "purchase recommendation",
            "legal/compliance/privacy/license clearance",
            "production readiness proof",
            "external action authorization",
        ],
        "modes": ["discover", "preflight"],
        "discover_inputs": ["objective", "query", "data_scope", "desired_capability_type", "freshness_preference"],
        "discover_outputs": [
            "top_candidates",
            "best_current_candidate",
            "source_traces",
            "missing_fields",
            "preliminary_route_decision",
            "next_action",
        ],
        "preflight_inputs": [
            "candidate_id",
            "intended_use",
            "available_metadata",
            "required_permissions",
            "organization_policy_optional",
        ],
        "preflight_outputs": [
            "route_decision",
            "reason",
            "missing_fields",
            "must_not_claim",
            "residualops_escalation",
            "next_action",
        ],
        "residualops_escalation": {
            "tool_manifest_risk": "AgentSec",
            "code_or_release_risk": "QIRA",
            "data_or_use_boundary_risk": "DataCapsule",
            "enterprise_receipt_tracking": "ResidualOps dashboard",
        },
        "claim_boundary": CLAIM_BOUNDARY,
        "private_kernel_not_disclosed": [
            "ranking weights",
            "thresholds",
            "anti-gaming rules",
            "provider priors",
            "private negative controls",
            "private probe seeds",
            "commercial routing policy",
            "real feedback memory",
            "customer-specific data",
        ],
    }


def validate_capability_card(card: dict[str, Any]) -> list[str]:
    required = [
        "schema",
        "name",
        "package",
        "version",
        "mcp_name",
        "type",
        "primary_users",
        "best_for",
        "not_for",
        "modes",
        "discover_inputs",
        "discover_outputs",
        "preflight_inputs",
        "preflight_outputs",
        "claim_boundary",
        "private_kernel_not_disclosed",
    ]
    missing = [key for key in required if key not in card]
    if card.get("version") != VERSION:
        missing.append("version_mismatch")
    if card.get("mcp_name") != MCP_NAME:
        missing.append("mcp_name_mismatch")
    if "discover" not in card.get("modes", []):
        missing.append("discover_mode")
    if "preflight" not in card.get("modes", []):
        missing.append("preflight_mode")
    return missing


def capability_card_markdown(card: dict[str, Any] | None = None) -> str:
    card = card or build_capability_card()
    best_for = "\n".join(f"- {item}" for item in card["best_for"])
    not_for = "\n".join(f"- {item}" for item in card["not_for"])
    boundary = "\n".join(f"- `{item}`" for item in card["claim_boundary"])
    return f"""# AOI Capability Card

AOI helps AI agents find source-traced capability/tool/API/MCP candidates for an objective, then preflight those candidates before use.

Package: `{card['package']}`  
Version: `{card['version']}`  
MCP name: `{card['mcp_name']}`  
Type: `{card['type']}`

## Best For

{best_for}

## Not For

{not_for}

## Modes

- `discover`: return useful source-traced candidates, missing fields, preliminary route decisions, and next actions.
- `preflight`: separate tool availability from use authorization before an agent recommends or executes anything.

## Claim Boundary

{boundary}

Private ranking weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, real feedback memory, and customer-specific data remain private and are not included in this card.
"""


def write_capability_card() -> dict[str, Any]:
    card = build_capability_card()
    write_json(CAPABILITY_CARD_PATH, card)
    write_text(CAPABILITY_CARD_MD_PATH, capability_card_markdown(card))
    return card


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Write capability card artifacts.")
    args = parser.parse_args()
    card = write_capability_card() if args.write else build_capability_card()
    missing = validate_capability_card(card)
    print(f"capability_card: {'PASS' if not missing else 'HOLD'} missing={len(missing)}")


if __name__ == "__main__":
    main()

