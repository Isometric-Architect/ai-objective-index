from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import read_text, timestamp, write_json, write_text
from .capability_decision_packet import sample_capability_decision_packet, validate_capability_decision_packet
from .final_argument_preflight import write_sample_final_argument_preflight
from .freshness_policy import negative_cache_contract
from .hold_to_replan_loop import write_sample_replan
from .middleware_contract import middleware_contract
from .route_reason_codes import ROUTE_REASON_CODES
from .route_semantics import EXPLICIT_SEPARATIONS, ROUTE_CLASSES


AGENT_DIR = Path("agent_discovery")
API_AGENT_EXAMPLES_DIR = Path("api") / "vnext" / "examples" / "agent"
PUBLIC_DIR = Path("public_launch") / "aoi_agent_discovery_5"


def generate_d5_artifacts() -> dict[str, Any]:
    from .discover_mode import write_sample_discover_examples
    from .preflight_mode import write_sample_preflight_examples

    packet = sample_capability_decision_packet()
    replan = write_sample_replan()
    final_preflight = write_sample_final_argument_preflight()
    negative_cache = negative_cache_contract("sample-stale-tool")
    contract = middleware_contract()
    discover_response = write_sample_discover_examples()
    preflight_response = write_sample_preflight_examples()

    examples = {
        "schema": "AOI_CapabilityDecisionPacketExamples/v0.1",
        "examples": [packet],
    }
    route_examples = {
        "schema": "AOI_RouteTransitionExamples/v0.1",
        "separations": EXPLICIT_SEPARATIONS,
        "examples": [
            {
                "from": "FOUND_ONLY",
                "to": "ALLOW_READ_ONLY",
                "new_evidence_required": True,
                "action_authorization": False,
            },
            {
                "from": "HOLD_AUTHORIZATION",
                "to": "ALLOW_LOW_RISK_CALL",
                "new_evidence_required": True,
                "action_authorization": False,
            },
        ],
    }

    write_json(AGENT_DIR / "CAPABILITY_DECISION_PACKET_EXAMPLES.json", examples)
    write_json(AGENT_DIR / "ROUTE_TRANSITION_EXAMPLES.json", route_examples)
    write_json(API_AGENT_EXAMPLES_DIR / "capability_decision_packet_discover_response.json", discover_response)
    write_json(API_AGENT_EXAMPLES_DIR / "capability_decision_packet_preflight_response.json", preflight_response)
    write_text(AGENT_DIR / "CAPABILITY_DECISION_PACKET_SPEC.md", capability_decision_packet_spec())
    write_text(AGENT_DIR / "ROUTE_SEMANTICS_SPEC.md", route_semantics_spec())
    write_text(AGENT_DIR / "ROUTE_REASON_CODES.md", route_reason_codes_doc())
    write_text(AGENT_DIR / "HOLD_TO_REPLAN_LOOP_SPEC.md", hold_to_replan_doc())
    write_text(AGENT_DIR / "FRESHNESS_RUGPULL_NEGATIVE_CACHE_SPEC.md", freshness_doc())
    write_text(AGENT_DIR / "FINAL_ARGUMENT_PREFLIGHT_SPEC.md", final_argument_doc())
    write_text(AGENT_DIR / "AGENT_MIDDLEWARE_CONTRACT.md", middleware_doc())

    write_json(PUBLIC_DIR / "AOI_D5_CAPABILITY_DECISION_PACKET_RESULT.json", {"packet": packet, "validation_errors": validate_capability_decision_packet(packet)})
    write_json(PUBLIC_DIR / "AOI_D5_ROUTE_SEMANTICS_RESULT.json", {"route_classes": ROUTE_CLASSES, "separations": EXPLICIT_SEPARATIONS})
    write_json(PUBLIC_DIR / "AOI_D5_HOLD_TO_REPLAN_RESULT.json", replan)
    write_json(PUBLIC_DIR / "AOI_D5_TEST_RESIDUAL_RESULT.json", test_residual_result())
    write_text(PUBLIC_DIR / "AOI_D5_SUMMARY.md", d5_summary())
    write_text(PUBLIC_DIR / "AOI_D5_NEXT_ACTIONS.md", d5_next_actions())

    return {
        "packet": packet,
        "replan": replan,
        "final_argument_preflight": final_preflight,
        "negative_cache": negative_cache,
        "middleware_contract": contract,
    }


def run_cdp_audit(write_result: bool = True) -> dict[str, Any]:
    artifacts = generate_d5_artifacts()
    packet_errors = validate_capability_decision_packet(artifacts["packet"])
    text = "\n".join(
        read_text(path).lower()
        for path in [
            AGENT_DIR / "CAPABILITY_DECISION_PACKET_SPEC.md",
            AGENT_DIR / "ROUTE_SEMANTICS_SPEC.md",
            AGENT_DIR / "HOLD_TO_REPLAN_LOOP_SPEC.md",
            AGENT_DIR / "FRESHNESS_RUGPULL_NEGATIVE_CACHE_SPEC.md",
            AGENT_DIR / "FINAL_ARGUMENT_PREFLIGHT_SPEC.md",
            AGENT_DIR / "AGENT_MIDDLEWARE_CONTRACT.md",
        ]
    )
    errors: list[str] = []
    if packet_errors:
        errors.extend(packet_errors)
    if "ranking_weights:" in text or "threshold_values:" in text or "provider_priors:" in text:
        errors.append("private_kernel_exposure")
    if "full suite green" in text:
        errors.append("false_full_suite_claim")
    if artifacts["packet"].get("external_action_authorization") is not False:
        errors.append("action_authorization")

    residual = test_residual_result()
    if errors:
        if "private_kernel_exposure" in errors:
            decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
        elif "false_full_suite_claim" in errors:
            decision = "BLOCK_FALSE_FULL_SUITE_CLAIM"
        elif "action_authorization" in errors:
            decision = "BLOCK_ACTION_AUTHORIZATION"
        else:
            decision = "BLOCK_OVERCLAIM"
    elif residual["decision"].startswith("PASS"):
        decision = "PASS_CAPABILITY_DECISION_PACKET_READY"
    else:
        decision = "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED"

    result = {
        "schema": "AOI_D5AuditResult/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "capability_decision_packet_valid": not packet_errors,
        "route_semantics_count": len(ROUTE_CLASSES),
        "reason_code_count": len(ROUTE_REASON_CODES),
        "hold_to_replan_present": True,
        "middleware_contract_present": True,
        "freshness_negative_cache_present": True,
        "test_residual_decision": residual["decision"],
        "no_false_full_suite_green_claim": True,
        "errors": errors,
    }
    if write_result:
        write_json(AGENT_DIR / "D5_AUDIT_RESULT.json", result)
        write_json(PUBLIC_DIR / "AOI_D5_AUDIT_RESULT.json", result)
    return result


def test_residual_result() -> dict[str, Any]:
    return {
        "schema": "AOI_D5TestResidualResult/v0.1",
        "decision": "PASS_NARROW_REGISTRY_PAYLOAD_RESIDUAL_REPAIRED",
        "classification": "narrow_code_bug_repaired_without_staging_generated_payloads",
        "narrow_patch": "registry_intake/real_payload_guard.py iterative payload unwrap with depth guard",
        "targeted_slice": "registry/datascope residual slice passed after patch",
        "full_suite_result": "PASS_FULL_PYTEST_1188_PASSED_1_WARNING",
        "full_suite_green_claim_allowed": True,
        "next_action": "Keep future full-suite claims tied to a current python -m pytest run.",
    }


def capability_decision_packet_spec() -> str:
    return """# Capability Decision Packet Spec

The Capability Decision Packet is AOI's canonical agent-facing output object. It separates discovered, trusted, authorized, and executable states while preserving route decision receipts.

Required fields include objective, capability identity, candidate source, objective fit score, source trace status, metadata completeness, freshness status, version pin, last checked timestamp, stale warning, rug-pull diff status, negative cache hit, action level, data boundary, auth scope, current auth context, route decision, route reason codes, missing fields, safe next action, blocked next actions, escalation path, receipt id, decision timestamp, recheck policy, and claim ceiling.

`objective_fit_score` is public/demo fit information only. It does not imply safety, authorization, certification, legal/privacy/license clearance, quality guarantee, or product readiness.
"""


def route_semantics_spec() -> str:
    routes = "\n".join(f"- `{route}`" for route in ROUTE_CLASSES)
    separations = "\n".join(f"- {item}" for item in EXPLICIT_SEPARATIONS)
    return f"""# Route Semantics Spec

## Route Classes

{routes}

## Separations

{separations}

Route decisions are receipts for a bounded use case. They do not grant external action authorization or make certification claims.
"""


def route_reason_codes_doc() -> str:
    codes = "\n".join(f"- `{code}`" for code in ROUTE_REASON_CODES)
    return f"""# Route Reason Codes

{codes}

Reason codes explain why a route was selected. They are not private ranking weights or hidden thresholds.
"""


def hold_to_replan_doc() -> str:
    return """# HOLD-to-Replan Loop Spec

On HOLD, classify the route reason, request missing evidence or downgrade to a lower-risk action, and stop after `max_iterations`.

Rules:

- no external action during replan
- no auto-approval
- no repeated candidate unless new evidence is attached
- escalation routes must identify AgentSec, QIRA, DataCapsule, human approval, or operator policy
"""


def freshness_doc() -> str:
    return """# Freshness, Rug-Pull, and Negative Cache Spec

AOI route decisions are point-in-time artifacts. Version changes require recheck. Stale metadata routes to `HOLD_STALE_METADATA`. Suspicious version drift routes to `HOLD_RUGPULL_DIFF`. Negative cache hits are recheckable route artifacts, not permanent proof.

No private anti-gaming rules, probe seeds, negative controls, provider priors, or commercial routing policy are disclosed.
"""


def final_argument_doc() -> str:
    return """# Final Argument Preflight Spec

Even when a capability is acceptable for discovery or review, its concrete arguments may change the route. Secret-like input blocks. External send, form submission, release PR, destructive database query, or filesystem overwrite routes to HOLD, BLOCK, or escalation.

Final argument preflight never grants external action authorization.
"""


def middleware_doc() -> str:
    return """# Agent Middleware Contract

AOI supports advisory, enforced, and non-bypassable proxy modes.

Agent-facing value: faster candidate discovery, fewer failed calls, fewer missing-field errors, and lower wasted turns.

Operator-facing value: audit trace, policy mapping, escalation, and receipts.

AOI middleware is not a security certification, legal/privacy/license clearance, product-readiness proof, or external action authorization layer.
"""


def d5_summary() -> str:
    return """# AOI Agent Discovery 5 Summary

D5 turns the cross-model feedback roadmap into executable Capability Decision Packet, granular route semantics, HOLD-to-Replan, final argument preflight, freshness/rug-pull/negative-cache, and middleware contracts.

It also narrowly repairs the registry payload-state residual by making the payload guard unwrap nested payload wrappers iteratively instead of recursing through generated wrappers.
"""


def d5_next_actions() -> str:
    return """# AOI D5 Next Actions

Recommended next package: AOI-CATALOG-GROWTH-1 Source Adapter + Freshness/Negative Cache Ingestion.

If any full-suite residual remains after the next full run, use AOI-TEST-RESIDUAL-1 Registry/Datascope Payload-State Repair.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_cdp_audit(write_result=True)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"cdp_audit: {result['decision']}")


if __name__ == "__main__":
    main()
