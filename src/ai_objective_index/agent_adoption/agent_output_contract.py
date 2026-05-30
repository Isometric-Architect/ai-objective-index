from __future__ import annotations

from pathlib import Path
from typing import Any

from . import write_json
from .discover_mode import discover_capabilities, sample_discover_request
from .preflight_mode import preflight_capability, sample_preflight_request


OUTPUT_CONTRACT_PATH = Path("agent_discovery") / "AGENT_OUTPUT_SCHEMA_EXAMPLES.json"

REQUIRED_OUTPUT_KEYS = [
    "objective",
    "mode",
    "candidates",
    "route_decision",
    "reason",
    "missing_fields",
    "next_action",
    "must_not_claim",
    "residualops_escalation",
    "freshness",
]


def build_output_contract_examples() -> dict[str, Any]:
    discover_request = sample_discover_request()
    discover_response = discover_capabilities(discover_request)
    preflight_request = sample_preflight_request()
    preflight_response = preflight_capability(preflight_request)
    return {
        "schema": "AOI_AgentOutputContractExamples/v0.1",
        "required_output_keys": REQUIRED_OUTPUT_KEYS,
        "discover_request": discover_request,
        "discover_response": discover_response,
        "preflight_request": preflight_request,
        "preflight_response": preflight_response,
        "ordinary_agent_bad_behavior_example": {
            "behavior": "The agent picks the first registry-looking tool and recommends using it before checking permissions.",
            "why_bad": "It confuses availability with authorization and treats metadata as proof.",
        },
        "corrected_aoi_behavior_example": {
            "behavior": "The agent returns useful HOLD candidates, exposes missing fields, then runs preflight before recommendation or use.",
            "route_decision": preflight_response["route_decision"],
            "next_action": preflight_response["next_action"],
        },
    }


def validate_output_contract(payload: dict[str, Any]) -> list[str]:
    response = payload.get("discover_response", {})
    return [key for key in REQUIRED_OUTPUT_KEYS if key not in response]


def write_output_contract_examples() -> dict[str, Any]:
    payload = build_output_contract_examples()
    write_json(OUTPUT_CONTRACT_PATH, payload)
    return payload

