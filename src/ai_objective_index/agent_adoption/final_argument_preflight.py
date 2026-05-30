from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from . import timestamp, write_json
from .capability_decision_packet import build_capability_decision_packet


FINAL_ARGUMENT_PREFLIGHT_RESPONSE_PATH = (
    Path("api") / "vnext" / "examples" / "agent" / "final_argument_preflight_response.json"
)


def preflight_arguments(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    text = f"{tool_name} {arguments}".lower()
    sql_text = str(arguments.get("sql", "")).lower()
    if any(marker in text for marker in ("sk-", "ghp_", "hf_", "private key", "api_key")):
        route = "BLOCK_SECRET_OR_PRIVATE_DATA"
        reason = "SECRET_LIKE_INPUT"
    elif tool_name == "filesystem.write" and any(key in arguments for key in ("overwrite", "path")):
        route = "HOLD_POLICY_CLARITY" if not arguments.get("confirmed") else "BLOCK_DESTRUCTIVE_ACTION"
        reason = "DESTRUCTIVE_ACTION"
    elif tool_name == "github.create_pr" and arguments.get("release") is True:
        route = "ESCALATE_QIRA"
        reason = "CODE_RELEASE_REQUIRES_QIRA"
    elif tool_name == "email.send" and arguments.get("recipient"):
        route = "ESCALATE_HUMAN_APPROVAL"
        reason = "EXTERNAL_SEND"
    elif tool_name == "database.query" and re.search(r"\b(update|delete|drop)\b", sql_text):
        route = "BLOCK_DESTRUCTIVE_ACTION"
        reason = "DESTRUCTIVE_ACTION"
    elif tool_name == "browser.submit_form":
        route = "ESCALATE_HUMAN_APPROVAL"
        reason = "EXTERNAL_SEND"
    else:
        route = "ALLOW_READ_ONLY"
        reason = "OBJECTIVE_MATCH"
    packet = build_capability_decision_packet(
        objective=f"Preflight arguments for {tool_name}",
        capability_id=tool_name.replace(".", "-"),
        capability_name=tool_name,
        route_decision=route,
        missing_fields=[] if route == "ALLOW_READ_ONLY" else ["argument_risk_review"],
        safe_next_action="Proceed only within read-only bounds." if route == "ALLOW_READ_ONLY" else "Repair or escalate arguments before use.",
        stale=False,
    )
    packet["route_reason_codes"] = [reason]
    return {
        "schema": "AOI_FinalArgumentPreflightPacket/v0.1",
        "generated_at": timestamp(),
        "tool_name": tool_name,
        "route_decision": route,
        "reason_code": reason,
        "capability_decision_packet": packet,
        "external_action_authorization": False,
    }


def write_sample_final_argument_preflight() -> dict[str, Any]:
    result = preflight_arguments("email.send", {"recipient": "external@example.invalid", "body": "draft only"})
    write_json(FINAL_ARGUMENT_PREFLIGHT_RESPONSE_PATH, result)
    return result
