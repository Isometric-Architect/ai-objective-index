from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from .capability_adapter import search_capability_trust_cards


def build_capability_trust_report(
    query: str,
    objective: str,
    domain: str = "mixed_ai_tools",
    data_scope: str = "sample",
    limit: int = 10,
) -> dict[str, Any]:
    objective_card, cards, warnings = search_capability_trust_cards(
        query=query,
        objective=objective,
        domain=domain,
        data_scope=data_scope,
        limit=limit,
    )
    decision_counts = Counter(card.route_decision.decision for card in cards)
    no_trace_count = sum(1 for card in cards if card.evidence_summary.source_trace_count == 0)
    hold_count = sum(1 for key, value in decision_counts.items() if key.startswith("HOLD") for _ in range(value))
    block_count = sum(1 for key, value in decision_counts.items() if key.startswith("BLOCK") for _ in range(value))
    allow_count = sum(1 for key, value in decision_counts.items() if key.startswith("ALLOW") for _ in range(value))
    top_holds = [
        {"object_id": card.object_id, "name": card.name, "decision": card.route_decision.decision, "reason": card.route_decision.reason}
        for card in cards
        if card.route_decision.decision.startswith("HOLD")
    ][:5]
    return {
        "schema": "AOI_CapabilityTrustReport/v0.1",
        "query": query,
        "objective": objective,
        "domain": domain,
        "data_scope": data_scope,
        "generated_at": datetime.now(UTC).isoformat(),
        "objective_card": objective_card.model_dump(mode="json", by_alias=True),
        "trust_cards": [card.model_dump(mode="json", by_alias=True) for card in cards],
        "summary": {
            "candidate_count": len(cards),
            "allow_count": allow_count,
            "hold_count": hold_count,
            "block_count": block_count,
            "no_source_trace_count": no_trace_count,
            "route_decision_counts": dict(decision_counts),
            "top_holds": top_holds,
            "claim_ceiling": "source-traced capability candidate; not verified; not security certified; not a quality guarantee",
        },
        "warnings": warnings,
        "known_limits": [
            "Offline local trust report only.",
            "No probe execution, gateway execution, live security scanning, crawling, or external LLM call was performed.",
            "ALLOW labels do not mean verified, safe, security certified, quality guaranteed, or purchase-ready.",
        ],
        "not_asserted": [
            "security certification",
            "quality guarantee",
            "supplier verification",
            "product readiness",
            "purchasing advice",
            "action permission",
        ],
    }
