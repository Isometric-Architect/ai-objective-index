from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import timestamp, write_json
from .capability_decision_packet import sample_capability_decision_packet


HOLD_TO_REPLAN_RESPONSE_PATH = Path("api") / "vnext" / "examples" / "agent" / "hold_to_replan_response.json"


def replan_for_hold(packet: dict[str, Any] | None = None, max_iterations: int = 3) -> dict[str, Any]:
    packet = packet or sample_capability_decision_packet()
    route = str(packet.get("route_decision", ""))
    repair = _repair_policy(route)
    return {
        "schema": "AOI_HOLDToReplanLoop/v0.1",
        "replan_id": f"replan-{packet.get('capability_id', 'candidate')}",
        "generated_at": timestamp(),
        "source_packet_id": packet.get("packet_id"),
        "hold_reason": route if route.startswith("HOLD") else "not_hold_route",
        "allowed_repair_actions": repair["allowed_repair_actions"],
        "forbidden_repair_actions": [
            "external action during replan",
            "auto-approval",
            "repeat same candidate without new evidence",
            "token or private data request",
            "certification or product-readiness claim",
        ],
        "alternative_candidate_query": repair["alternative_candidate_query"],
        "lower_risk_action": repair["lower_risk_action"],
        "escalation_path": repair["escalation_path"],
        "max_iterations": max_iterations,
        "stop_conditions": [
            "max_iterations reached",
            "blocked route encountered",
            "no new evidence available",
            "human or operator approval required",
        ],
        "no_auto_approval": True,
        "no_external_action": True,
        "no_repeated_candidate_without_new_evidence": True,
        "candidate_set_hold_next_action": (
            "Return candidate-set HOLD with missing fields and request evidence if max iterations are reached."
        ),
    }


def _repair_policy(route: str) -> dict[str, Any]:
    return {
        "HOLD_MISSING_FIELDS": {
            "allowed_repair_actions": ["ask for missing fields", "choose lower-risk read-only action"],
            "alternative_candidate_query": "Find candidates with complete permission and source-trace metadata.",
            "lower_risk_action": "ALLOW_DISCOVERY_ONLY",
            "escalation_path": "",
        },
        "HOLD_STALE_METADATA": {
            "allowed_repair_actions": ["refresh source trace", "choose alternate candidate"],
            "alternative_candidate_query": "Find candidates with fresher source traces.",
            "lower_risk_action": "ALLOW_DISCOVERY_ONLY",
            "escalation_path": "",
        },
        "HOLD_AUTHORIZATION": {
            "allowed_repair_actions": ["ask user or admin", "downgrade to read-only or draft-only"],
            "alternative_candidate_query": "Find candidates requiring no live credentials or write permissions.",
            "lower_risk_action": "ALLOW_DRAFT_ONLY",
            "escalation_path": "ESCALATE_HUMAN_APPROVAL",
        },
        "HOLD_SECURITY_REVIEW": {
            "allowed_repair_actions": ["escalate AgentSec", "request manifest"],
            "alternative_candidate_query": "Find source-traced candidates with lower manifest risk.",
            "lower_risk_action": "ALLOW_DISCOVERY_ONLY",
            "escalation_path": "ESCALATE_AGENTSEC",
        },
        "HOLD_PRIVACY_REVIEW": {
            "allowed_repair_actions": ["escalate DataCapsule", "request privacy/data boundary fields"],
            "alternative_candidate_query": "Find candidates with clearer data retention and privacy boundaries.",
            "lower_risk_action": "ALLOW_DISCOVERY_ONLY",
            "escalation_path": "ESCALATE_DATACAPSULE",
        },
        "HOLD_POLICY_CLARITY": {
            "allowed_repair_actions": ["escalate operator policy", "request organization policy"],
            "alternative_candidate_query": "Find candidates that satisfy known organization policy.",
            "lower_risk_action": "ALLOW_DRAFT_ONLY",
            "escalation_path": "ESCALATE_OPERATOR_POLICY",
        },
        "HOLD_RUGPULL_DIFF": {
            "allowed_repair_actions": ["mark negative cache candidate", "review version drift", "choose alternate candidate"],
            "alternative_candidate_query": "Find candidates without suspicious version or metadata drift.",
            "lower_risk_action": "ALLOW_DISCOVERY_ONLY",
            "escalation_path": "ESCALATE_AGENTSEC",
        },
    }.get(
        route,
        {
            "allowed_repair_actions": ["manual triage"],
            "alternative_candidate_query": "Find lower-risk source-traced candidates.",
            "lower_risk_action": "ALLOW_DISCOVERY_ONLY",
            "escalation_path": "ESCALATE_HUMAN_APPROVAL",
        },
    )


def write_sample_replan() -> dict[str, Any]:
    result = replan_for_hold()
    write_json(HOLD_TO_REPLAN_RESPONSE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = write_sample_replan() if args.sample else replan_for_hold()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"hold_to_replan_loop: {result['hold_reason']} max_iterations={result['max_iterations']}")


if __name__ == "__main__":
    main()
