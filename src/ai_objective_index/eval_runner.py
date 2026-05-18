from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from .mcp_tools import search_objectives
from .scoring import score_object
from .seed_loader import (
    load_golden_queries as core_load_golden_queries,
    load_sample_index,
    load_source_traces,
)
from .store import ObjectiveIndexStore


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_output_path(path: str | Path) -> Path:
    destination = Path(path)
    if destination.is_absolute():
        return destination
    return _repo_root() / destination


def _tokens(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        text = " ".join(str(item) for item in value)
    elif isinstance(value, dict):
        text = " ".join(str(item) for pair in value.items() for item in pair)
    else:
        text = str(value)
    return set(re.findall(r"[a-z0-9]+", text.lower().replace("_", " ")))


def load_golden_queries(path: str | Path = "data/golden_queries.json") -> list[dict[str, Any]]:
    return core_load_golden_queries(path)


def _expected_terms(query_record: dict[str, Any]) -> set[str]:
    terms: set[str] = set()
    for key in (
        "expected_capabilities",
        "expected_keywords",
        "expected_object_types",
        "expected_domains",
        "expected_focus",
    ):
        if key in query_record:
            terms |= _tokens(query_record.get(key))
    return terms


def _top_result_text(results: list[dict[str, Any]]) -> set[str]:
    text_bits = []
    for result in results:
        text_bits.extend(
            [
                result.get("object_id"),
                result.get("name"),
                result.get("object_type"),
                result.get("summary"),
                result.get("rank_reason"),
                result.get("missing_fields"),
            ]
        )
    return _tokens(text_bits)


def _structural_pass(top_result: dict[str, Any] | None) -> bool:
    if not top_result:
        return False
    required = [
        "object_id",
        "objective_score",
        "rank_reason",
        "status",
        "missing_fields",
        "source_urls",
    ]
    return all(key in top_result and top_result[key] is not None for key in required)


def run_golden_query(query_record: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    query = query_record.get("query") or query_record.get("objective") or ""
    objective = query_record.get("objective")
    domain = query_record.get("domain")
    response = search_objectives(
        query=query,
        domain=domain,
        objective=objective,
        limit=limit,
    )
    results = response.get("results", [])
    top_results = results[:limit]
    top_result = top_results[0] if top_results else None

    objects = load_sample_index()
    traces = load_source_traces()
    store = ObjectiveIndexStore(objects, traces)
    traced_object_ids = {trace.object_id for trace in traces}
    result_ids = [result["object_id"] for result in top_results if result.get("object_id")]
    scored_results = []
    for object_id in result_ids:
        action_object = store.get_object(object_id)
        if action_object is None:
            continue
        scored_results.append(
            score_object(
                action_object,
                query=query,
                objective=objective,
                traces=store.get_traces(object_id),
            )
        )

    score_values = [result.get("objective_score", 0) for result in top_results]
    confidence_values = [result.get("confidence", 0) for result in top_results]
    warnings = sorted(
        {
            warning
            for result in top_results
            for warning in result.get("warnings", [])
        }
    )
    status_counts = dict(Counter(str(result.get("status", "unknown")) for result in top_results))
    expected_terms = _expected_terms(query_record)
    relevance_pass: bool | str
    relevance_overlap: list[str]
    if expected_terms:
        overlap = expected_terms & _top_result_text(top_results)
        relevance_overlap = sorted(overlap)
        relevance_pass = bool(overlap)
    else:
        relevance_overlap = []
        relevance_pass = "not_evaluated"

    source_trace_coverage = (
        sum(1 for object_id in result_ids if object_id in traced_object_ids) / len(result_ids)
        if result_ids
        else 0.0
    )

    return {
        "query_id": query_record.get("query_id"),
        "query": query,
        "objective": objective,
        "domain": domain,
        "top_k": limit,
        "result_count": len(top_results),
        "top_results": top_results,
        "average_objective_score": round(mean(score_values), 2) if score_values else 0.0,
        "average_confidence": round(mean(confidence_values), 4) if confidence_values else 0.0,
        "source_trace_coverage": round(source_trace_coverage, 4),
        "missing_fields_count": sum(len(result.get("missing_fields", [])) for result in top_results),
        "status_counts": status_counts,
        "warnings": warnings,
        "structural_pass": _structural_pass(top_result),
        "relevance_pass": relevance_pass,
        "relevance_overlap": relevance_overlap,
        "scored_result_count": len(scored_results),
    }


def run_all_golden_queries(limit: int = 5) -> dict[str, Any]:
    query_records = load_golden_queries()
    results = [run_golden_query(record, limit=limit) for record in query_records]
    query_count = len(results)
    structural_pass_count = sum(1 for result in results if result["structural_pass"])
    evaluated_relevance = [
        result for result in results if isinstance(result.get("relevance_pass"), bool)
    ]
    relevance_pass_count = sum(1 for result in evaluated_relevance if result["relevance_pass"])
    avg_scores = [result["average_objective_score"] for result in results]
    avg_confidences = [result["average_confidence"] for result in results]
    avg_coverage = [result["source_trace_coverage"] for result in results]

    return {
        "version": "0.1.0-package-4",
        "generated_at": datetime.now(UTC).isoformat(),
        "query_count": query_count,
        "structural_pass_count": structural_pass_count,
        "structural_pass_rate": round(structural_pass_count / query_count, 4)
        if query_count
        else 0.0,
        "relevance_evaluated_count": len(evaluated_relevance),
        "relevance_pass_count": relevance_pass_count,
        "relevance_pass_rate": round(relevance_pass_count / len(evaluated_relevance), 4)
        if evaluated_relevance
        else None,
        "average_objective_score": round(mean(avg_scores), 2) if avg_scores else 0.0,
        "average_confidence": round(mean(avg_confidences), 4) if avg_confidences else 0.0,
        "average_source_trace_coverage": round(mean(avg_coverage), 4) if avg_coverage else 0.0,
        "results": results,
    }


def save_eval_results(
    results: dict[str, Any], path: str | Path = "data/eval_results.json"
) -> None:
    destination = _resolve_output_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    results = run_all_golden_queries()
    save_eval_results(results)
    print("Golden query eval complete")
    print(f"query_count: {results['query_count']}")
    print(f"structural_pass_count: {results['structural_pass_count']}")
    print(f"average_objective_score: {results['average_objective_score']}")
    print("wrote: data/eval_results.json")


if __name__ == "__main__":
    main()

