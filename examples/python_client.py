from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "http://127.0.0.1:8000"


def get_json(path: str):
    try:
        with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        print("AOI API is not running. Start it with: python -m ai_objective_index.api")
        return None


def main() -> None:
    query = urllib.parse.quote("cheap image generation API")
    search = get_json(f"/search?query={query}&limit=3&data_scope=sample")
    if not search:
        return

    integrated = get_json(f"/search?query={query}&limit=3&data_scope=integrated")
    curated = get_json(f"/search?query={query}&limit=3&data_scope=curated")
    public_beta = get_json(f"/search?query={query}&limit=3&data_scope=public_beta")
    mcp_query = urllib.parse.quote("browser automation MCP")
    mcp_registry = get_json(f"/search?query={mcp_query}&limit=3&data_scope=mcp_registry")
    public_beta_mcp = get_json(f"/search?query={mcp_query}&limit=3&data_scope=public_beta_mcp")
    print(json.dumps(search, indent=2))
    if integrated:
        print(json.dumps({"integrated_example": integrated}, indent=2))
    if curated:
        print(json.dumps({"curated_example": curated}, indent=2))
    if public_beta:
        print(json.dumps({"public_beta_example": public_beta}, indent=2))
    if mcp_registry:
        print(json.dumps({"mcp_registry_example": mcp_registry}, indent=2))
    if public_beta_mcp:
        print(
            json.dumps(
                {
                    "public_beta_mcp_example": public_beta_mcp,
                    "note": "public_beta_mcp rows are registry metadata candidates, not verified or security certified; it may be empty in fixture mode.",
                },
                indent=2,
            )
        )
    results = search.get("results", [])
    if not results:
        return

    object_id = results[0]["object_id"]
    traces = get_json(f"/objects/{object_id}/source-trace?data_scope=sample")
    if traces:
        print(json.dumps(traces, indent=2))


if __name__ == "__main__":
    main()
