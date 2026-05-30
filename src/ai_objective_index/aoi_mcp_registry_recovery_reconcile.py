from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_marker_sync import CANONICAL_MCP_NAME, OUTPUT_DIR, PACKAGE_NAME, TARGET_VERSION, repo_root, write_json
from .aoi_mcp_registry_recovery_publish import OUTPUT_PATH as PUBLISH_OUTPUT_PATH


OUTPUT_PATH = OUTPUT_DIR / "AOI_MCP_REGISTRY_RECOVERY_RECONCILE_RESULT.json"
SEARCH_URL = "https://registry.modelcontextprotocol.io/v0/servers"


def _read_publish() -> dict[str, Any]:
    full = repo_root() / PUBLISH_OUTPUT_PATH
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _fetch_registry_search(timeout: int = 20) -> dict[str, Any]:
    query = urllib.parse.urlencode({"search": CANONICAL_MCP_NAME})
    request = urllib.request.Request(f"{SEARCH_URL}?{query}", headers={"User-Agent": "ai-objective-index-aoi-030a2"})
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


def run_recovery_reconcile(
    fetcher: Callable[[], dict[str, Any]] = _fetch_registry_search,
    publish_result: dict[str, Any] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    publish = publish_result if publish_result is not None else _read_publish()
    response = fetcher() if publish.get("decision") in {"PASS_MCP_REGISTRY_RECOVERY_PUBLISHED", "HOLD_ALREADY_PUBLISHED_OR_VERSION_EXISTS"} else {"checked": False, "body": "", "status_code": None, "error": "publish not confirmed"}
    body = str(response.get("body") or "")
    matches = _matches(body)
    errors: list[str] = []
    warnings: list[str] = []
    if all(matches.values()):
        decision = "PASS_MCP_REGISTRY_RECOVERY_RECONCILED"
    elif response.get("checked") and matches.get("server_name"):
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("Registry entry was found but version/package/claim boundary did not match.")
    elif publish.get("decision") == "PASS_MCP_REGISTRY_RECOVERY_PUBLISHED":
        decision = "HOLD_REGISTRY_PROPAGATION"
        warnings.append("Publish was attempted successfully, but registry search did not yet show the expected entry.")
    else:
        decision = "HOLD_PUBLISH_NOT_CONFIRMED"
        warnings.append("Registry publish has not been confirmed.")
    result = {
        "schema": "AOI_MCPRegistryRecoveryReconcileResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
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
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_recovery_reconcile()
    print(f"aoi_mcp_registry_recovery_reconcile: {result['decision']}")


if __name__ == "__main__":
    main()
