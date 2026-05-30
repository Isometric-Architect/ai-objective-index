from __future__ import annotations

from typing import Any


def middleware_contract() -> dict[str, Any]:
    return {
        "schema": "AOI_AgentMiddlewareContract/v0.1",
        "modes": {
            "advisory": "Agent reads AOI route decision and may replan.",
            "enforced": "Operator places AOI before the tool executor.",
            "non_bypassable_proxy": "Tool call must pass AOI final argument preflight before execution.",
        },
        "agent_facing_value": [
            "faster candidate discovery",
            "fewer failed calls",
            "fewer missing-field errors",
            "lower wasted turns",
        ],
        "operator_facing_value": [
            "audit trace",
            "policy mapping",
            "escalation",
            "receipt",
        ],
        "external_action_authorization": False,
        "security_certification": False,
        "legal_privacy_license_clearance": False,
        "product_readiness_claim": False,
    }
