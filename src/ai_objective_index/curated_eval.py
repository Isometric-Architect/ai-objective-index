from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from .curated_loader import load_curated_objects, load_curated_source_traces
from .scoring import score_object
from .store import ObjectiveIndexStore


DEFAULT_OUTPUT = Path("data/curated/curated_eval_results_v0_1.json")
QUERIES = [
    "AI API with pricing docs",
    "MCP server with source traces",
    "commercial use AI tool",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_curated_eval() -> dict[str, Any]:
    objects = load_curated_objects()
    traces = load_curated_source_traces()
    warnings: list[str] = []
    if not objects:
        warnings.append("No curated objects available yet.")
    if any("placeholder" in str(getattr(item, "notes", "")).lower() for item in objects):
        warnings.append("Curated dataset currently contains placeholder objects; public beta scope may be empty.")

    store = ObjectiveIndexStore(objects, traces)
    results: list[dict[str, Any]] = []
    scores: list[float] = []
    for query in QUERIES:
        rows = []
        for candidate in store.search_objects(query, limit=5):
            score = score_object(candidate, query=query, traces=store.get_traces(candidate.object_id))
            row = {
                "object_id": candidate.object_id,
                "name": candidate.name,
                "status": score.status,
                "objective_score": score.objective_score,
                "warnings": score.warnings,
            }
            rows.append(row)
            scores.append(score.objective_score)
        results.append({"query": query, "result_count": len(rows), "results": rows})

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "query_count": len(QUERIES),
        "object_count": len(objects),
        "result_count": sum(item["result_count"] for item in results),
        "average_score": round(mean(scores), 2) if scores else 0.0,
        "warnings": warnings,
        "results": results,
    }
    return payload


def save_curated_eval(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT,
) -> Path:
    payload = results or run_curated_eval()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    payload = run_curated_eval()
    path = save_curated_eval(payload)
    print(
        "Curated eval: "
        f"objects={payload['object_count']} "
        f"queries={payload['query_count']} "
        f"results={payload['result_count']} "
        f"output={path}"
    )


if __name__ == "__main__":
    main()
