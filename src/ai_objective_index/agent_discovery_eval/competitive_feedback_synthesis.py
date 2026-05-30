from __future__ import annotations

import argparse
import json

from . import (
    COMPETITIVE_SYNTHESIS_PATH,
    CROSS_MODEL_SUMMARY_PATH,
    DISCOVERY_4_NEXT_ACTIONS_PATH,
    DISCOVERY_4_SUMMARY_PATH,
    read_json,
    timestamp,
    write_text,
)
from .cross_model_feedback_classifier import run_cross_model_feedback_classifier
from .route_semantics_roadmap import run_route_semantics_roadmap


def synthesis_markdown(summary: dict[str, object]) -> str:
    consensus = "\n".join(f"- {item}" for item in summary.get("cross_model_consensus", []))
    tensions = "\n".join(f"- {item}" for item in summary.get("disagreements_or_tensions", []))
    deltas = "\n".join(f"- {item}" for item in summary.get("roadmap_deltas", []))
    return f"""# Competitive Feedback Synthesis

Discovery 4 ingests redacted manual feedback from Gemini, GPT-5.5 Thinking, and Claude Opus 4.8 High. The feedback is local/offline and does not call external model APIs.

## What All Models Agree On

{consensus}

## What Models Disagree On

{tensions}

## Roadmap Changes

{deltas}

## What Should Not Change

- AOI should remain discovery-first for ordinary agents.
- AOI should keep pre-use trust routing separate from execution.
- AOI should preserve explicit claim boundaries.
- AOI should not become just another registry.
- AOI should combine a fast discovery UX with a pre-use trust backend.

## Competitive Interpretation

The strongest differentiator is not the registry surface by itself. It is the receipt-carrying Capability Decision Packet that separates found, trusted, authorized, and executable states. This lets AOI serve ordinary agents that need speed while still giving operators a routeable control point.

## Claim Boundaries

- This synthesis is not a security certification.
- This synthesis is not product readiness proof.
- This synthesis is not legal, privacy, license, or compliance clearance.
- This synthesis does not authorize external action.
"""


def next_actions_markdown() -> str:
    return """# AOI Agent Discovery 4 Next Actions

Recommended next package: AOI-AGENT-DISCOVERY-5 Capability Decision Packet + Route Semantics Hardening.

Secondary package: AOI-CATALOG-GROWTH-1 Source Adapter + Freshness/Negative Cache Ingestion.

The first package should come next because all three external feedback summaries converge on route semantics, decision receipts, and discovery-versus-execution separation as the product wedge. Catalog growth matters, but it benefits more once the packet and route semantics are harder to misuse.
"""


def summary_markdown(summary: dict[str, object]) -> str:
    return f"""# AOI Agent Discovery 4 Summary

Discovery 4 converts manual external model feedback into redacted local packets and a product roadmap synthesis.

- Feedback packets: {summary.get('packet_count')}
- Route/preflight/governance model count: {summary.get('route_preflight_governance_model_count')}
- Adoption friction or latency model count: {summary.get('adoption_friction_or_latency_model_count')}
- Recommended next package: {summary.get('recommended_next_package')}

This is not a live external LLM benchmark and not a full-suite green claim.
"""


def run_competitive_feedback_synthesis(write_result: bool = True) -> dict[str, object]:
    summary = read_json(CROSS_MODEL_SUMMARY_PATH)
    if not summary:
        summary = run_cross_model_feedback_classifier(write_result=True)
    run_route_semantics_roadmap(write_result=True)
    result = {
        "schema": "AOI_CompetitiveFeedbackSynthesis/v0.1",
        "generated_at": timestamp(),
        "source_summary_ref": str(CROSS_MODEL_SUMMARY_PATH).replace("\\", "/"),
        "recommended_next_package": summary.get("recommended_next_package"),
        "consensus_count": len(summary.get("cross_model_consensus", [])),
        "roadmap_delta_count": len(summary.get("roadmap_deltas", [])),
        "claim_boundary": summary.get("claim_boundary", []),
    }
    if write_result:
        write_text(COMPETITIVE_SYNTHESIS_PATH, synthesis_markdown(summary))
        write_text(DISCOVERY_4_SUMMARY_PATH, summary_markdown(summary))
        write_text(DISCOVERY_4_NEXT_ACTIONS_PATH, next_actions_markdown())
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_competitive_feedback_synthesis(write_result=True)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"competitive_feedback_synthesis: recommendation={result['recommended_next_package']}")


if __name__ == "__main__":
    main()
