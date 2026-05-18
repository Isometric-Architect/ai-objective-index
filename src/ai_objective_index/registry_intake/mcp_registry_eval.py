from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from ai_objective_index.scoring import score_object
from ai_objective_index.store import ObjectiveIndexStore

from .mcp_registry_loader import load_registry_objects, load_registry_source_traces


DEFAULT_OUTPUT = Path("data/registry/mcp_registry_eval_results_v0_1.json")
QUERIES = [
    "browser automation MCP server",
    "web search MCP server",
    "document extraction MCP server",
    "vector database MCP server",
    "code execution MCP server",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def run_mcp_registry_eval() -> dict[str, Any]:
    objects = load_registry_objects()
    traces = load_registry_source_traces()
    fixture_only = any(bool(getattr(item, "fixture_only", False)) for item in objects)
    store = ObjectiveIndexStore(objects, traces)
    scores: list[float] = []
    results: list[dict[str, Any]] = []
    for query in QUERIES:
        rows = []
        for candidate in store.search_objects(query, domain="mcp_servers", limit=5):
            score = score_object(candidate, query=query, traces=store.get_traces(candidate.object_id))
            rows.append(
                {
                    "object_id": candidate.object_id,
                    "name": candidate.name,
                    "status": score.status,
                    "objective_score": score.objective_score,
                    "warnings": score.warnings,
                }
            )
            scores.append(score.objective_score)
        results.append({"query": query, "result_count": len(rows), "results": rows})
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "fixture_only": fixture_only,
        "query_count": len(QUERIES),
        "object_count": len(objects),
        "result_count": sum(item["result_count"] for item in results),
        "average_score": round(mean(scores), 2) if scores else 0.0,
        "results": results,
        "warnings": ["Fixture-only registry data is not public beta promoted."] if fixture_only else [],
    }


def save_mcp_registry_eval(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT,
) -> Path:
    payload = results or run_mcp_registry_eval()
    destination = _resolve(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    payload = run_mcp_registry_eval()
    path = save_mcp_registry_eval(payload)
    print(
        "MCP registry eval: "
        f"objects={payload['object_count']} "
        f"queries={payload['query_count']} "
        f"results={payload['result_count']} "
        f"fixture_only={payload['fixture_only']} "
        f"output={path}"
    )


if __name__ == "__main__":
    main()

