from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from .generated_loader import load_generated_objects
from .integrated_store import get_store_for_scope
from .report_metrics import compute_source_trace_coverage
from .scoring import score_object
from .seed_loader import load_sample_index


INTEGRATED_QUERIES = [
    "cheap image generation API with commercial use terms",
    "browser automation MCP server with source traces",
    "OCR API with free tier and rate limits",
    "developer-friendly API docs and pricing clarity",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path(path: str | Path) -> Path:
    destination = Path(path)
    if destination.is_absolute():
        return destination
    return _repo_root() / destination


def run_integrated_eval(scope: str = "integrated", limit: int = 5) -> dict[str, Any]:
    store = get_store_for_scope(scope)
    objects = store.list_objects()
    query_results = []
    all_scores = []
    top_names = []

    for query in INTEGRATED_QUERIES:
        candidates = store.search_objects(query, limit=limit)
        rows = []
        for candidate in candidates:
            score = score_object(
                candidate,
                query=query,
                traces=store.get_traces(candidate.object_id),
            )
            row = {
                "object_id": candidate.object_id,
                "name": candidate.name,
                "status": score.status,
                "objective_score": score.objective_score,
                "rank_reason": score.rank_reason,
                "missing_fields": score.missing_fields,
            }
            rows.append(row)
            all_scores.append(score.objective_score)
        rows.sort(key=lambda item: item["objective_score"], reverse=True)
        if rows:
            top_names.append(rows[0]["name"])
        query_results.append({"query": query, "result_count": len(rows), "top_results": rows})

    traces = []
    for action_object in objects:
        traces.extend(store.get_traces(action_object.object_id))
    generated_object_count = len(load_generated_objects()) if scope in {"generated", "integrated"} else 0
    sample_object_count = len(load_sample_index()) if scope in {"sample", "integrated"} else 0

    return {
        "version": "0.2-package-6c",
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": scope,
        "query_count": len(INTEGRATED_QUERIES),
        "result_count": sum(item["result_count"] for item in query_results),
        "average_score": round(mean(all_scores), 2) if all_scores else 0.0,
        "status_counts": dict(Counter(str(item.status) for item in objects)),
        "generated_object_count": generated_object_count,
        "sample_object_count": sample_object_count,
        "source_trace_coverage": compute_source_trace_coverage(objects, traces),
        "top_result_names": top_names,
        "results": query_results,
        "read_only": True,
        "network_fetch": False,
    }


def save_integrated_eval_results(
    results: dict[str, Any],
    path: str | Path = "data/generated/integrated_eval_results_v0_2.json",
) -> Path:
    destination = _path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_integrated_eval()
    path = save_integrated_eval_results(results)
    print("Integrated eval complete")
    print(f"query_count: {results['query_count']}")
    print(f"result_count: {results['result_count']}")
    print(f"average_score: {results['average_score']}")
    print(f"source_trace_coverage: {results['source_trace_coverage']}")
    print(f"wrote: {path}")


if __name__ == "__main__":
    main()

