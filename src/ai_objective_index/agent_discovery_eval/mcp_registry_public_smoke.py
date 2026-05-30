from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from . import (
    CANONICAL_MCP_NAME,
    MCP_REGISTRY_PUBLIC_SMOKE_PATH,
    PACKAGE_NAME,
    TARGET_VERSION,
    timestamp,
    write_json,
)


SEARCH_URL = "https://registry.modelcontextprotocol.io/v0/servers"


def _fetch_registry(timeout: int = 20) -> dict[str, Any]:
    query = urllib.parse.urlencode({"search": CANONICAL_MCP_NAME})
    request = urllib.request.Request(
        f"{SEARCH_URL}?{query}",
        headers={"User-Agent": "ai-objective-index-agent-discovery-3"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return {"checked": False, "status_code": exc.code, "body": "", "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError) as exc:
        return {"checked": False, "status_code": None, "body": "", "error": str(exc)[:800]}
    return {"checked": True, "status_code": 200, "body": body, "error": ""}


def _matches(body: str) -> dict[str, bool]:
    lower = body.lower()
    return {
        "server_name": CANONICAL_MCP_NAME.lower() in lower,
        "package": PACKAGE_NAME.lower() in lower,
        "version": TARGET_VERSION.lower() in lower,
        "registry_type_pypi": "pypi" in lower,
        "no_certification_claim": "security certified" not in lower and "production ready" not in lower,
    }


def run_mcp_registry_public_smoke(
    fetcher: Callable[[], dict[str, Any]] = _fetch_registry,
    write_result: bool = True,
) -> dict[str, Any]:
    response = fetcher()
    body = str(response.get("body") or "")
    matches = _matches(body)
    warnings: list[str] = []
    errors: list[str] = []
    if response.get("checked") and all(matches.values()):
        decision = "PASS_MCP_REGISTRY_PUBLIC_SMOKE"
    elif response.get("checked") and matches.get("server_name"):
        decision = "BLOCK_REGISTRY_METADATA_MISMATCH"
        errors.append("Registry entry was found but expected version, package, or claim boundary did not match.")
    else:
        decision = "HOLD_REGISTRY_PROPAGATION"
        warnings.append("Registry search did not show the expected public entry yet or network was unavailable.")

    result = {
        "schema": "AOI_MCPRegistryPublicSmokeResult/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "server_name": CANONICAL_MCP_NAME,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "registry_search_url": f"{SEARCH_URL}?search={urllib.parse.quote(CANONICAL_MCP_NAME)}",
        "registry_checked": bool(response.get("checked")),
        "registry_status_code": response.get("status_code"),
        "matches": matches,
        "token_printed": False,
        "publish_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(MCP_REGISTRY_PUBLIC_SMOKE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_mcp_registry_public_smoke()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"mcp_registry_public_smoke: {result['decision']}")


if __name__ == "__main__":
    main()
