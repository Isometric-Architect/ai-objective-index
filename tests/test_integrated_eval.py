import json
from pathlib import Path
from uuid import uuid4

from ai_objective_index.integrated_eval import run_integrated_eval, save_integrated_eval_results


def test_integrated_eval_writes_json() -> None:
    output_path = Path("data/generated") / f"integrated_eval_test_{uuid4().hex}.json"
    try:
        results = run_integrated_eval()
        written = save_integrated_eval_results(results, output_path)
        payload = json.loads(written.read_text(encoding="utf-8"))

        assert payload["query_count"] > 0
        assert "source_trace_coverage" in payload
        assert payload["generated_object_count"] >= 3
    finally:
        if output_path.exists():
            output_path.unlink()

