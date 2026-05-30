from __future__ import annotations

import argparse
import json
from typing import Any

from . import (
    CLAUDE_FEEDBACK_PACKET_PATH,
    GEMINI_FEEDBACK_PACKET_PATH,
    GPT55_FEEDBACK_PACKET_PATH,
    timestamp,
    write_json,
)
from .external_model_feedback_schema import FEEDBACK_PACKET_SCHEMA, validate_feedback_packet


MODEL_FEEDBACK_FIXTURES: dict[str, dict[str, Any]] = {
    "gemini": {
        "path": GEMINI_FEEDBACK_PACKET_PATH,
        "model_name": "Gemini",
        "overall_rating_if_present": "positive_direction_with_productization_blockers",
        "key_positive_findings": [
            "AOI is useful as AI-native capability discovery plus a pre-use trust router.",
            "The discover-first framing is stronger than treating AOI as only an audit gate.",
            "Machine-readable claim boundaries help ordinary agents avoid unsupported execution claims.",
        ],
        "key_adoption_blockers": [
            "data fragmentation",
            "latency penalty",
            "enterprise policy conflict",
            "stale metadata",
        ],
        "recommended_killer_features": [
            "self-healing or auto-correction when AOI identifies missing fields",
            "context-aware trust",
            "agent-native SDK/API",
            "adaptive governance",
            "recursive HOLD-to-Replan loop",
        ],
        "route_semantics_recommendations": [
            "Make HOLD productive by returning a replan path rather than a dead end.",
            "Adjust governance by context and action risk.",
        ],
        "freshness_or_rugpull_recommendations": [
            "Treat stale metadata as an explicit route reason.",
            "Attach refresh next actions instead of claiming live freshness.",
        ],
        "enterprise_or_operator_positioning": [
            "Offer policy-aware behavior for enterprise contexts without hiding uncertainty.",
        ],
        "claim_boundary_warnings": [
            "Do not imply AOI verifies providers or grants permission to execute tools.",
        ],
        "overclaim_risks": [
            "Agent-native trust routing could be overread as safety validation if the claim ceiling is not visible.",
        ],
        "direct_quotes_short_safe_only": [
            "Self-Healing / Auto-Correction",
            "Context-Aware Trust",
            "Adaptive Governance",
        ],
    },
    "gpt55": {
        "path": GPT55_FEEDBACK_PACKET_PATH,
        "model_name": "GPT-5.5 Thinking",
        "overall_rating_if_present": "positive_with_semantic_hardening_required",
        "key_positive_findings": [
            "AOI should not be framed as just registry or search.",
            "AOI can sit between an agent planner and a tool executor.",
            "The public message should emphasize finding the right capability fast.",
        ],
        "key_adoption_blockers": [
            "coarse ALLOW/HOLD/BLOCK labels",
            "agent confusion between discovery and execution readiness",
            "metadata treated as proof",
        ],
        "recommended_killer_features": [
            "Capability Decision Packet",
            "granular route semantics",
            "planner-to-executor preflight boundary",
        ],
        "route_semantics_recommendations": [
            "Split discovered, trusted, authorized, and executable states.",
            "Use route labels more granular than ALLOW/HOLD/BLOCK.",
        ],
        "freshness_or_rugpull_recommendations": [
            "Include timestamped route decisions and version-aware recheck policy.",
        ],
        "enterprise_or_operator_positioning": [
            "Externally say find the right capability fast.",
            "Internally enforce separation between discovered, trusted, authorized, and executable.",
        ],
        "claim_boundary_warnings": [
            "A candidate is not verified merely because it appears in a registry.",
            "A route decision is not action authorization.",
        ],
        "overclaim_risks": [
            "Route labels may sound stronger than the evidence unless the state machine is explicit.",
        ],
        "direct_quotes_short_safe_only": [
            "Capability Decision Packet",
            "Find the right capability fast.",
            "discovered, trusted, authorized, and executable",
        ],
    },
    "claude": {
        "path": CLAUDE_FEEDBACK_PACKET_PATH,
        "model_name": "Claude Opus 4.8 High",
        "overall_rating_if_present": "valid_direction_with_market_and_friction_risks",
        "key_positive_findings": [
            "The direction is valid for ordinary agents if discovery stays fast.",
            "AOI can have dual positioning as agent-facing discovery and operator-facing middleware.",
            "Receipt-carrying route decisions can differentiate AOI from a plain registry.",
        ],
        "key_adoption_blockers": [
            "beneficiary and consumer mismatch",
            "trust router trust regression",
            "rug-pull and freshness weakness",
            "incumbents in MCP gateway and security registry space",
            "too much friction from HOLD/BLOCK",
        ],
        "recommended_killer_features": [
            "fast discovery hot path",
            "lazy deeper preflight for committed candidates",
            "route decisions with receipts and timestamps",
            "negative cache",
            "rug-pull diff",
            "operator-enforced non-bypassable middleware option",
        ],
        "route_semantics_recommendations": [
            "Make HOLD the exception for low-risk read-only or idempotent cases.",
            "Carry timestamped receipts with route decisions.",
        ],
        "freshness_or_rugpull_recommendations": [
            "Add negative cache for known bad, deprecated, or untrusted candidates.",
            "Add rug-pull diff checks for suspicious version or metadata drift.",
        ],
        "enterprise_or_operator_positioning": [
            "Agent-facing fast discovery UX.",
            "Operator-facing non-bypassable pre-use middleware.",
        ],
        "claim_boundary_warnings": [
            "Do not become another registry or another gateway without a differentiated decision packet.",
        ],
        "overclaim_risks": [
            "Trust router trust regression if AOI decisions are not themselves auditable and freshness-bound.",
        ],
        "direct_quotes_short_safe_only": [
            "another registry",
            "another gateway",
            "negative cache",
            "rug-pull diff",
        ],
    },
}


def build_feedback_packet(model_key: str) -> dict[str, Any]:
    fixture = MODEL_FEEDBACK_FIXTURES[model_key]
    packet = {
        "schema": FEEDBACK_PACKET_SCHEMA,
        "packet_id": f"aoi-discovery-4-{model_key}-feedback",
        "generated_at": timestamp(),
        "model_name": fixture["model_name"],
        "prompt_set": "AOI-AGENT-DISCOVERY-3 manual external model feedback summary",
        "overall_rating_if_present": fixture["overall_rating_if_present"],
        "key_positive_findings": fixture["key_positive_findings"],
        "key_adoption_blockers": fixture["key_adoption_blockers"],
        "recommended_killer_features": fixture["recommended_killer_features"],
        "route_semantics_recommendations": fixture["route_semantics_recommendations"],
        "freshness_or_rugpull_recommendations": fixture["freshness_or_rugpull_recommendations"],
        "enterprise_or_operator_positioning": fixture["enterprise_or_operator_positioning"],
        "claim_boundary_warnings": fixture["claim_boundary_warnings"],
        "overclaim_risks": fixture["overclaim_risks"],
        "direct_quotes_short_safe_only": fixture["direct_quotes_short_safe_only"],
        "redaction_status": "PASS_REDACTED",
        "token_or_secret_detected": False,
        "external_llm_api_called": False,
        "raw_transcript_stored": False,
        "private_kernel_exposed": False,
        "claim_boundary": [
            "feedback is not product readiness proof",
            "feedback is not security certification",
            "feedback is not action authorization",
            "feedback is not legal, privacy, license, or compliance clearance",
        ],
    }
    packet["validation_errors"] = validate_feedback_packet(packet)
    return packet


def run_manual_cross_model_intake(write_result: bool = True) -> list[dict[str, Any]]:
    packets = [build_feedback_packet(key) for key in ("gemini", "gpt55", "claude")]
    if write_result:
        for key, packet in zip(("gemini", "gpt55", "claude"), packets, strict=True):
            write_json(MODEL_FEEDBACK_FIXTURES[key]["path"], packet)
    return packets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packets = run_manual_cross_model_intake(write_result=True)
    if args.json:
        print(json.dumps(packets, indent=2, ensure_ascii=False))
    else:
        print(f"manual_cross_model_intake: packets={len(packets)} redaction=PASS_REDACTED")


if __name__ == "__main__":
    main()
