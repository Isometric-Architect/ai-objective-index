from __future__ import annotations

from typing import Any

from .cdp_rest_adapters import attach_discover_cdp, attach_preflight_cdp


def add_cdp_to_mcp_discover_response(response: dict[str, Any]) -> dict[str, Any]:
    response = attach_discover_cdp(response)
    response["read_only"] = True
    response["action_authorization"] = False
    return response


def add_cdp_to_mcp_preflight_response(response: dict[str, Any]) -> dict[str, Any]:
    response = attach_preflight_cdp(response)
    response["read_only"] = True
    response["action_authorization"] = False
    return response
