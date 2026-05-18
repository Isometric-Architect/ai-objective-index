from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://registry.modelcontextprotocol.io"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _api_get(url: str, timeout: int = 10) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "AI-Objective-Index-Registry-Intake/0.1",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _limit_payload(payload: Any, max_servers: int) -> Any:
    if isinstance(payload, list):
        return payload[:max_servers]
    if isinstance(payload, dict):
        limited = dict(payload)
        for key in ("servers", "items", "data"):
            if isinstance(limited.get(key), list):
                limited[key] = limited[key][:max_servers]
                break
        return limited
    return payload


def fetch_registry_servers(
    base_url: str = DEFAULT_BASE_URL,
    max_servers: int = 50,
    allow_network: bool = False,
    timeout: int = 10,
) -> dict[str, Any]:
    """Fetch server metadata from the official MCP Registry API.

    Network is disabled by default. The function never parses HTML and never
    follows links beyond the fixed `/v0.1/servers` endpoint.
    """

    if not allow_network:
        url = f"{base_url.rstrip('/')}/v0.1/servers?limit={max(1, max_servers)}"
        return {
            "error": "Live network fetch disabled. Use fixture mode or pass allow_network=True.",
            "live_network_used": False,
            "source_url": url,
            "servers": [],
        }

    url = f"{base_url.rstrip('/')}/v0.1/servers?limit={max(1, max_servers)}"
    try:
        payload = _api_get(url, timeout=timeout)
        return {
            "source_url": url,
            "live_network_used": True,
            "payload": _limit_payload(payload, max(1, max_servers)),
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {
            "error": f"Registry fetch failed: {exc}",
            "live_network_used": False,
            "source_url": url,
            "servers": [],
        }


def fetch_server_latest(
    server_name: str,
    base_url: str = DEFAULT_BASE_URL,
    allow_network: bool = False,
    timeout: int = 10,
) -> dict[str, Any]:
    if not allow_network:
        return {
            "error": "Live network fetch disabled. Use fixture mode or pass allow_network=True.",
            "live_network_used": False,
            "server_name": server_name,
        }
    quoted = urllib.parse.quote(server_name.strip("/"), safe="")
    url = f"{base_url.rstrip('/')}/v0.1/servers/{quoted}/versions/latest"
    try:
        return {
            "source_url": url,
            "server_name": server_name,
            "live_network_used": True,
            "payload": _api_get(url, timeout=timeout),
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {
            "error": f"Registry latest-version fetch failed: {exc}",
            "source_url": url,
            "server_name": server_name,
            "live_network_used": False,
        }


def save_raw_registry_payload(
    payload: dict[str, Any],
    path: str | Path = "data/registry/mcp_registry_raw_v0_1.json",
) -> None:
    destination = _resolve(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_raw_registry_fixture(
    path: str | Path = "data/registry/mcp_registry_raw_fixture_v0_1.json",
) -> dict[str, Any]:
    resolved = _resolve(path)
    return json.loads(resolved.read_text(encoding="utf-8"))
