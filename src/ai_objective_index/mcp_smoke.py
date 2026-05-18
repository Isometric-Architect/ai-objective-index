from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import mcp_tools
from .mcp_compat import fetch, search
from .mcp_manifest import get_mcp_tool_manifest


DEFAULT_OUTPUT_PATH = Path("data/generated/mcp_smoke_result_v0_2.json")


def run_smoke(
    query: str = "cheap image generation API",
    data_scope: str = "sample",
    write_result: bool = True,
) -> dict[str, Any]:
    search_result = search(query=query, data_scope=data_scope, limit=5)
    top = search_result.get("results", [None])[0] if search_result.get("results") else None
    fetch_result = fetch(top["object_id"], data_scope=data_scope) if top else {}
    manifest = get_mcp_tool_manifest()
    tool_names = {tool["name"] for tool in manifest["tools"]}
    forbidden_actions = set(mcp_tools.FORBIDDEN_ACTIONS)
    forbidden_actions_exposed_as_tools = sorted(tool_names & forbidden_actions)
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "data_scope": data_scope,
        "query": query,
        "search_result_count": len(search_result.get("results", [])),
        "top_object_id": top.get("object_id") if top else None,
        "top_name": top.get("name") if top else None,
        "fetch_status": fetch_result.get("status") if fetch_result else "no_result",
        "source_trace_count": len(fetch_result.get("source_traces", [])) if fetch_result else 0,
        "missing_fields_count": len(fetch_result.get("missing_fields", [])) if fetch_result else 0,
        "forbidden_actions_exposed_as_tools": forbidden_actions_exposed_as_tools,
        "pass": bool(search_result.get("results")) and not forbidden_actions_exposed_as_tools,
        "limitations": mcp_tools.KNOWN_LIMITS,
        "forbidden_actions": mcp_tools.FORBIDDEN_ACTIONS,
    }
    if write_result:
        path = Path.cwd() / DEFAULT_OUTPUT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result["output_path"] = str(path)
    return result


def main() -> None:
    result = run_smoke()
    print(
        "MCP smoke: "
        f"pass={result['pass']} "
        f"results={result['search_result_count']} "
        f"top={result['top_name']} "
        f"forbidden_tool_overlap={len(result['forbidden_actions_exposed_as_tools'])}"
    )
    if result.get("output_path"):
        print(f"Saved MCP smoke result: {result['output_path']}")


if __name__ == "__main__":
    main()
