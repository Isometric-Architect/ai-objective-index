from __future__ import annotations

import argparse
import json

from . import (
    AGENT_OPERATOR_POSITIONING_PATH,
    CAPABILITY_DECISION_PACKET_DRAFT_PATH,
    FRESHNESS_RUGPULL_NOTES_PATH,
    HOLD_TO_REPLAN_SPEC_PATH,
    ROUTE_SEMANTICS_ROADMAP_PATH,
    timestamp,
    write_text,
)
from .external_model_feedback_schema import capability_decision_packet_fields, route_classes


SEPARATION_STATEMENTS = [
    "FOUND != TRUSTED",
    "TRUSTED != AUTHORIZED",
    "AUTHORIZED != EXECUTABLE",
    "route decision != security certification",
    "route decision != action authorization",
]


def route_semantics_markdown() -> str:
    routes = "\n".join(f"- `{route}`" for route in route_classes())
    statements = "\n".join(f"- {statement}" for statement in SEPARATION_STATEMENTS)
    return f"""# Route Semantics Roadmap

AOI route labels need to become more granular than ALLOW/HOLD/BLOCK so ordinary agents can move fast without confusing discovery with execution readiness.

## Route Classes

{routes}

## Required Separations

{statements}

## Design Notes

- `FOUND_ONLY` means AOI found a candidate, not that the candidate is trusted.
- `ALLOW_DISCOVERY_ONLY` is appropriate when an agent may summarize or compare candidates but must not call the tool.
- `ALLOW_READ_ONLY` is for low-risk inspection when source traces and permission boundaries are adequate.
- `ALLOW_DRAFT_ONLY` lets an agent prepare a plan, diff, or message without sending or mutating anything.
- `ALLOW_LOW_RISK_CALL` is reserved for narrow, idempotent, bounded calls with permission and data boundaries known.
- HOLD routes must include a next action and should be exception paths for low-risk read-only cases.
- BLOCK routes prevent the proposed action; they do not prove the candidate is globally unusable.
- ESCALATE routes send evidence to AgentSec, QIRA, DataCapsule, or human approval without authorizing external action.

This roadmap is a design draft. It is not a security certification, product readiness statement, or action authorization.
"""


def capability_decision_packet_markdown() -> str:
    fields = "\n".join(f"- `{field}`" for field in capability_decision_packet_fields())
    return f"""# Capability Decision Packet Draft

A Capability Decision Packet is a machine-readable receipt that lets an ordinary agent distinguish discovery usefulness from execution readiness.

## Required Fields

{fields}

## Public/Demo Scoring Boundary

- `objective_fit_score` may use transparent public/demo scoring only.
- Do not expose private ranking weights, thresholds, provider priors, private negative controls, private probe seeds, or commercial routing policy.
- Scores do not imply provider verification, security certification, legal clearance, or product readiness.

## Agent Use

The packet should travel between the planner and tool executor. The planner can compare candidates quickly; the executor receives route decisions, missing fields, blocked next actions, and recheck policy before any attempted use.
"""


def hold_to_replan_markdown() -> str:
    return """# HOLD-to-Replan Loop Spec

When AOI returns HOLD, the agent should not stop or silently skip the route decision. It should replan within explicit guards.

## Loop

1. Classify the HOLD reason.
2. If fields are missing, request fields or choose a lower-risk action.
3. If metadata is stale, refresh source traces or use an alternate candidate.
4. If authorization is missing, ask the user or admin, or downgrade to read/draft mode.
5. If tool or manifest risk is present, escalate to AgentSec.
6. If code or release risk is present, escalate to QIRA.
7. If data or use-boundary risk is present, escalate to DataCapsule.
8. If `max_iterations` is reached, return candidate-set HOLD with a concrete next action.

## Loop Guards

- `max_iterations` must be explicit.
- Do not repeat the same candidate unless new evidence is attached.
- Do not perform external action during replan.
- Do not auto-approve a HOLD route.
- Do not treat feedback as external action authorization.
"""


def agent_operator_positioning_markdown() -> str:
    return """# Agent / Operator Dual Positioning

AOI should keep two compatible product postures.

## Agent-Facing UX

- Fast capability discovery.
- Google-like candidate finding for ordinary agents.
- Lower wasted turns from missing-field repair.
- Reduced failed calls by separating availability from authorization.

## Operator-Facing Control

- Pre-use middleware or proxy before the tool executor.
- Advisory mode where agents can read route decisions.
- Enforced mode where operators place AOI in the execution path.
- Enterprise value from audit trace, escalation, and policy mapping.

The operator layer is not a certification layer. It records route decisions and evidence boundaries; it does not grant blanket permission to execute.
"""


def freshness_notes_markdown() -> str:
    return """# Freshness, Rug-Pull Diff, and Negative Cache Notes

- AOI route decisions are point-in-time artifacts and expire.
- Version changes require recheck.
- Stale metadata routes to `HOLD_STALE_METADATA`.
- Suspicious version or metadata drift routes to `HOLD_RUGPULL_DIFF` or a BLOCK route depending on severity.
- A negative cache stores known bad, deprecated, or untrusted candidates.
- Negative cache entries are not permanent proof; they are recheckable advisory or route artifacts.
- AOI should not expose private anti-gaming details, private probe seeds, private negative controls, provider priors, or commercial routing policy.
- Freshness claims must say when evidence was checked; they must not claim live freshness unless a live check actually occurred.
"""


def run_route_semantics_roadmap(write_result: bool = True) -> dict[str, object]:
    result = {
        "schema": "AOI_RouteSemanticsRoadmap/v0.1",
        "generated_at": timestamp(),
        "route_classes": route_classes(),
        "capability_decision_packet_fields": capability_decision_packet_fields(),
        "separation_statements": SEPARATION_STATEMENTS,
        "hold_to_replan_guards": [
            "max_iterations",
            "no repeated candidate unless new evidence",
            "no external action during replan",
            "no auto-approval",
        ],
        "claim_boundary": [
            "route decision is not security certification",
            "route decision is not action authorization",
            "Capability Decision Packet is not product readiness proof",
        ],
    }
    if write_result:
        write_text(ROUTE_SEMANTICS_ROADMAP_PATH, route_semantics_markdown())
        write_text(CAPABILITY_DECISION_PACKET_DRAFT_PATH, capability_decision_packet_markdown())
        write_text(HOLD_TO_REPLAN_SPEC_PATH, hold_to_replan_markdown())
        write_text(AGENT_OPERATOR_POSITIONING_PATH, agent_operator_positioning_markdown())
        write_text(FRESHNESS_RUGPULL_NOTES_PATH, freshness_notes_markdown())
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_route_semantics_roadmap(write_result=True)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"route_semantics_roadmap: route_classes={len(result['route_classes'])}")


if __name__ == "__main__":
    main()
