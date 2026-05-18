import json
from pathlib import Path

from ai_objective_index.eval_runner import (
    run_all_golden_queries,
    save_eval_results,
)


def test_run_all_golden_queries_returns_results():
    results = run_all_golden_queries(limit=3)

    assert results["query_count"] > 0
    assert results["results"]
    first = results["results"][0]
    assert "query" in first
    assert "top_results" in first
    assert "average_objective_score" in first
    assert "source_trace_coverage" in first
    assert "structural_pass" in first


def test_save_eval_results_writes_json():
    results = run_all_golden_queries(limit=2)
    path = Path("data/__tmp_eval_results_test.json")

    try:
        save_eval_results(results, path)

        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["query_count"] == results["query_count"]
    finally:
        if path.exists():
            path.unlink()
