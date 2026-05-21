from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .package_metadata_audit import MCP_NAME
from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave11_mcp_registry" / "MCP_REGISTRY_POST_PUBLISH_VERIFY_RESULT.json"
SEARCH_URL = "https://registry.modelcontextprotocol.io/v0/servers"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _fetch_registry_search(timeout: int = 20) -> dict[str, Any]:
    query = urllib.parse.urlencode({"search": MCP_NAME})
    request = urllib.request.Request(f"{SEARCH_URL}?{query}", headers={"User-Agent": "ai-objective-index-mcp-registry-verify"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return {"checked": False, "status_code": exc.code, "body": "", "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeError) as exc:
        return {"checked": False, "status_code": None, "body": "", "error": str(exc)[:1000]}
    return {"checked": True, "status_code": 200, "body": raw, "error": ""}


def run_mcp_registry_post_publish_verify(
    fetcher: Callable[[], dict[str, Any]] = _fetch_registry_search,
    write_result: bool = True,
) -> dict[str, Any]:
    response = fetcher()
    warnings: list[str] = []
    errors: list[str] = []
    body = str(response.get("body") or "")
    found = MCP_NAME in body
    if not response.get("checked"):
        decision = "HOLD_REGISTRY_VERIFY_NOT_CHECKED"
        warnings.append("MCP Registry search could not be checked.")
    elif found:
        decision = "PASS_REGISTRY_ENTRY_FOUND"
    else:
        decision = "HOLD_REGISTRY_ENTRY_NOT_FOUND_YET"
        warnings.append("Registry search was reachable but the AOI entry was not found yet.")
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "server_name": MCP_NAME,
        "registry_search_url": f"{SEARCH_URL}?search={urllib.parse.quote(MCP_NAME)}",
        "registry_entry_found": found,
        "checked": bool(response.get("checked")),
        "status_code": response.get("status_code"),
        "error": response.get("error", ""),
        "body_excerpt": body[:1000],
        "mcp_registry_submission_performed": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_mcp_registry_post_publish_verify()
    print(f"mcp_registry_post_publish_verify: {result['decision']}")


if __name__ == "__main__":
    main()
