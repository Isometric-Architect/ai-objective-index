from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_final_common import (
    CANONICAL_MCP_NAME,
    FINAL_MCP_PUBLISH_PATH,
    FINAL_MCP_RECONCILE_PATH,
    PACKAGE_NAME,
    TARGET_VERSION,
    now,
    read_json,
    write_json,
)


SEARCH_URL = "https://registry.modelcontextprotocol.io/v0/servers"
RECONCILABLE_PUBLISH_DECISIONS = {
    "PASS_MCP_REGISTRY_PUBLISH_CONFIRMED",
    "ALREADY_PUBLISHED_OR_VERSION_EXISTS",
}


def _fetch_registry_search(timeout: int = 20) -> dict[str, Any]:
    query = urllib.parse.urlencode({"search": CANONICAL_MCP_NAME})
    request = urllib.request.Request(f"{SEARCH_URL}?{query}", headers={"User-Agent": "ai-objective-index-aoi-030a2-final"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return {"checked": False, "status_code": exc.code, "body": "", "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError) as exc:
        return {"checked": False, "status_code": None, "body": "", "error": sanitize(exc)}
    return {"checked": True, "status_code": 200, "body": body, "error": ""}


def _matches(body: str) -> dict[str, bool]:
    lower = body.lower()
    return {
        "server_name": CANONICAL_MCP_NAME.lower() in lower,
        "version": TARGET_VERSION.lower() in lower,
        "package": PACKAGE_NAME.lower() in lower,
        "no_certification_claim": "security certified" not in lower and "production ready" not in lower,
    }


def run_final_mcp_registry_reconcile(
    fetcher: Callable[[], dict[str, Any]] = _fetch_registry_search,
    publish_result: dict[str, Any] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    publish = publish_result if publish_result is not None else read_json(FINAL_MCP_PUBLISH_PATH)
    if publish.get("decision") in RECONCILABLE_PUBLISH_DECISIONS:
        response = fetcher()
    else:
        response = {"checked": False, "body": "", "status_code": None, "error": "publish not confirmed"}
    body = str(response.get("body") or "")
    matches = _matches(body)
    errors: list[str] = []
    warnings: list[str] = []

    if all(matches.values()):
        decision = "PASS_MCP_REGISTRY_ENTRY_VERIFIED"
    elif response.get("checked") and matches.get("server_name"):
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("Registry entry was found but version/package/claim boundary did not match.")
    elif publish.get("decision") == "PASS_MCP_REGISTRY_PUBLISH_CONFIRMED":
        decision = "HOLD_REGISTRY_PROPAGATION"
        warnings.append("Publish was confirmed locally, but registry search did not yet show the expected entry.")
    else:
        decision = "HOLD_REGISTRY_PUBLISH_NOT_CONFIRMED"
        warnings.append("Registry publish has not been confirmed.")

    result = {
        "schema": "AOI_030A2FinalMCPRegistryReconcileResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "publish_decision": publish.get("decision"),
        "submission_performed": bool(publish.get("submission_performed")),
        "registry_checked": bool(response.get("checked")),
        "registry_status_code": response.get("status_code"),
        "registry_search_url": f"{SEARCH_URL}?search={urllib.parse.quote(CANONICAL_MCP_NAME)}",
        "matches": matches,
        "token_printed": False,
        "can_claim_certification": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(FINAL_MCP_RECONCILE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_mcp_registry_reconcile()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"aoi_030a2_final_mcp_registry_reconcile: {result['decision']}")


if __name__ == "__main__":
    main()

