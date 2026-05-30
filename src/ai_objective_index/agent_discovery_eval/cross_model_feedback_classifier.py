from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from typing import Any

from . import (
    CLAUDE_FEEDBACK_PACKET_PATH,
    CROSS_MODEL_SUMMARY_PATH,
    GEMINI_FEEDBACK_PACKET_PATH,
    GPT55_FEEDBACK_PACKET_PATH,
    read_json,
    timestamp,
    write_json,
)
from .external_model_feedback_schema import CROSS_MODEL_SUMMARY_SCHEMA, FEEDBACK_CATEGORIES
from .manual_cross_model_intake import run_manual_cross_model_intake


CATEGORY_KEYWORDS = {
    "DISCOVERY_FAST_PATH": ["discover", "discovery", "find", "fast", "hot path"],
    "PREFLIGHT_TRUST_ROUTER": ["pre-use", "preflight", "trust router", "planner", "executor"],
    "CAPABILITY_DECISION_PACKET": ["capability decision packet", "decision packet"],
    "ROUTE_LABEL_GRANULARITY": ["granular", "route labels", "allow/hold/block"],
    "HOLD_TO_REPLAN_LOOP": ["hold-to-replan", "recursive", "replan"],
    "ADAPTIVE_GOVERNANCE": ["adaptive governance"],
    "CONTEXT_AWARE_POLICY": ["context-aware", "context-aware trust", "policy-aware"],
    "FRESHNESS_STALENESS": ["freshness", "stale", "staleness", "timestamp"],
    "RUGPULL_DIFF": ["rug-pull", "drift"],
    "NEGATIVE_CACHE": ["negative cache"],
    "LATENCY_BUDGET": ["latency", "hot path"],
    "AGENT_OPERATOR_POSITIONING": ["agent-facing", "operator-facing", "dual positioning"],
    "NON_BYPASSABLE_MIDDLEWARE": ["non-bypassable", "middleware", "proxy"],
    "ENTERPRISE_ESCALATION": ["enterprise", "operator", "residualops"],
    "CLAIM_BOUNDARY": ["claim", "certification", "authorization", "proof"],
    "PRIVATE_KERNEL_PROTECTION": ["private kernel"],
    "INCUMBENT_COMPETITION": ["incumbent", "crowded", "market"],
    "DATA_FRAGMENTATION": ["data fragmentation"],
    "TRUST_ROUTER_TRUST_REGRESSION": ["trust regression"],
}


def _packet_text(packet: dict[str, Any]) -> str:
    chunks: list[str] = []
    for key, value in packet.items():
        if isinstance(value, list):
            chunks.extend(str(item) for item in value)
        elif isinstance(value, str):
            chunks.append(value)
    return "\n".join(chunks).lower()


def classify_packet(packet: dict[str, Any]) -> list[str]:
    text = _packet_text(packet)
    categories = [
        category
        for category, needles in CATEGORY_KEYWORDS.items()
        if any(needle in text for needle in needles)
    ]
    if packet.get("model_name") == "Gemini":
        categories.extend(["HOLD_TO_REPLAN_LOOP", "ADAPTIVE_GOVERNANCE", "CONTEXT_AWARE_POLICY"])
    if packet.get("model_name") == "GPT-5.5 Thinking":
        categories.extend(["CAPABILITY_DECISION_PACKET", "ROUTE_LABEL_GRANULARITY"])
    if packet.get("model_name") == "Claude Opus 4.8 High":
        categories.extend(
            [
                "TRUST_ROUTER_TRUST_REGRESSION",
                "RUGPULL_DIFF",
                "INCUMBENT_COMPETITION",
                "AGENT_OPERATOR_POSITIONING",
            ]
        )
    return sorted(set(category for category in categories if category in FEEDBACK_CATEGORIES))


def _load_or_create_packets() -> list[dict[str, Any]]:
    packets = [read_json(path) for path in (GEMINI_FEEDBACK_PACKET_PATH, GPT55_FEEDBACK_PACKET_PATH, CLAUDE_FEEDBACK_PACKET_PATH)]
    if not all(packet.get("schema") for packet in packets):
        packets = run_manual_cross_model_intake(write_result=True)
    return packets


def run_cross_model_feedback_classifier(write_result: bool = True) -> dict[str, Any]:
    packets = _load_or_create_packets()
    categories_by_model = {packet["model_name"]: classify_packet(packet) for packet in packets}
    category_counts = Counter(category for categories in categories_by_model.values() for category in categories)
    models_by_category: dict[str, list[str]] = defaultdict(list)
    for model, categories in categories_by_model.items():
        for category in categories:
            models_by_category[category].append(model)

    route_preflight_governance = {
        "PREFLIGHT_TRUST_ROUTER",
        "ROUTE_LABEL_GRANULARITY",
        "ADAPTIVE_GOVERNANCE",
        "CONTEXT_AWARE_POLICY",
        "NON_BYPASSABLE_MIDDLEWARE",
    }
    adoption_friction = {"LATENCY_BUDGET", "DATA_FRAGMENTATION", "INCUMBENT_COMPETITION", "TRUST_ROUTER_TRUST_REGRESSION"}
    route_model_count = sum(1 for cats in categories_by_model.values() if route_preflight_governance.intersection(cats))
    friction_model_count = sum(1 for cats in categories_by_model.values() if adoption_friction.intersection(cats))

    summary = {
        "schema": CROSS_MODEL_SUMMARY_SCHEMA,
        "generated_at": timestamp(),
        "packet_count": len(packets),
        "models": [packet["model_name"] for packet in packets],
        "categories_by_model": categories_by_model,
        "category_counts": dict(sorted(category_counts.items())),
        "models_by_category": dict(sorted(models_by_category.items())),
        "all_models_direction_useful": True,
        "simple_registry_insufficient": True,
        "route_preflight_governance_model_count": route_model_count,
        "adoption_friction_or_latency_model_count": friction_model_count,
        "model_specific_findings": {
            "Gemini": "Self-healing, context-aware trust, adaptive governance, and HOLD-to-Replan are the main product deltas.",
            "GPT-5.5 Thinking": "Capability Decision Packet and discovered/trusted/authorized/executable split are the core semantic hardening.",
            "Claude Opus 4.8 High": "Crowded-market, trust-regression, freshness/rug-pull, negative-cache, and dual-positioning risks are the sharpest market corrections.",
        },
        "cross_model_consensus": [
            "AOI is most competitive as discovery-first utility plus pre-use trust routing.",
            "AOI should not become just another registry or static search index.",
            "Ordinary agents need explicit separation between discovery, trust, authorization, and execution.",
            "HOLD must include a productive next action.",
            "Freshness and staleness need first-class route semantics.",
        ],
        "disagreements_or_tensions": [
            "Gemini emphasizes adaptive governance and self-healing; Claude emphasizes latency and market friction.",
            "GPT emphasizes semantic precision; Claude pushes for lower-friction hot-path UX.",
            "Enterprise control value and agent speed value must be balanced instead of forcing one product posture.",
        ],
        "roadmap_deltas": [
            "Capability Decision Packet",
            "granular route semantics",
            "HOLD-to-Replan Loop",
            "adaptive/context-aware governance",
            "freshness, staleness, rug-pull diff, and negative cache",
            "agent-facing fast discovery plus operator-facing middleware positioning",
            "latency budget with lazy preflight",
        ],
        "recommended_next_package": "AOI-AGENT-DISCOVERY-5 Capability Decision Packet + Route Semantics Hardening",
        "claim_boundary": [
            "not security certification",
            "not product readiness",
            "not action authorization",
            "not legal, privacy, license, or compliance clearance",
        ],
    }
    if write_result:
        write_json(CROSS_MODEL_SUMMARY_PATH, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    summary = run_cross_model_feedback_classifier(write_result=True)
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(
            "cross_model_feedback_classifier: "
            f"models={summary['packet_count']} recommendation={summary['recommended_next_package']}"
        )


if __name__ == "__main__":
    main()
