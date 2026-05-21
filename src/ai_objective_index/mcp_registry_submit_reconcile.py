from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .package_metadata_audit import MCP_NAME
from .real_pypi_upload_gate import PACKAGE_NAME, TARGET_VERSION, _repo_root


OUTPUT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_REGISTRY_SUBMIT_RECONCILE_RESULT.json"
SUBMIT_RESULT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_REGISTRY_SUBMIT_RESULT.json"
SEARCH_URL = "https://registry.modelcontextprotocol.io/v0/servers"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _fetch_registry_search(timeout: int = 20) -> dict[str, Any]:
    query = urllib.parse.urlencode({"search": MCP_NAME})
    request = urllib.request.Request(f"{SEARCH_URL}?{query}", headers={"User-Agent": "ai-objective-index-mcp-registry-reconcile"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return {"checked": False, "status_code": exc.code, "body": "", "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError) as exc:
        return {"checked": False, "status_code": None, "body": "", "error": str(exc)[:1000]}
    return {"checked": True, "status_code": 200, "body": body, "error": ""}


def _registry_matches(body: str) -> dict[str, bool]:
    lower = body.lower()
    return {
        "server_name": MCP_NAME.lower() in lower,
        "version": TARGET_VERSION.lower() in lower,
        "package": PACKAGE_NAME.lower() in lower,
    }


def run_mcp_registry_submit_reconcile(
    fetcher: Callable[[], dict[str, Any]] = _fetch_registry_search,
    write_result: bool = True,
) -> dict[str, Any]:
    submit = _read_json(SUBMIT_RESULT_PATH)
    response = fetcher()
    body = str(response.get("body") or "")
    matches = _registry_matches(body)
    found = all(matches.values())
    warnings: list[str] = []
    errors: list[str] = []

    if found:
        decision = "PASS_REGISTRY_ENTRY_VERIFIED"
    elif response.get("checked") and matches["server_name"]:
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("Registry entry found but version/package metadata did not match expected values.")
    elif submit.get("result_token") == "PUBLISH_SUCCESS":
        decision = "HOLD_REGISTRY_PROPAGATION"
        warnings.append("Publish result exists, but registry entry is not visible yet.")
    else:
        decision = "HOLD_PUBLISH_NOT_CONFIRMED"
        warnings.append("Publish success has not been confirmed and registry evidence is absent.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "publish_result_token": submit.get("result_token"),
        "submission_performed": bool(submit.get("submission_performed")),
        "registry_checked": bool(response.get("checked")),
        "registry_status_code": response.get("status_code"),
        "registry_search_url": f"{SEARCH_URL}?search={urllib.parse.quote(MCP_NAME)}",
        "matches": matches,
        "registry_entry_verified": found,
        "token_printed": False,
        "mcp_registry_submission_performed": bool(submit.get("submission_performed")),
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_mcp_registry_submit_reconcile()
    print(f"mcp_registry_submit_reconcile: {result['decision']}")


if __name__ == "__main__":
    main()
