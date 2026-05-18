import json
from pathlib import Path

from ai_objective_index.negative_control_runner import (
    run_false_closure_controls,
    save_false_closure_results,
)


def test_negative_control_runner_passes_and_writes() -> None:
    results = run_false_closure_controls()
    assert results["control_count"] >= 10
    assert results["false_BOX"] == 0
    assert results["forbidden_promotions"] == 0
    assert results["every_hold_has_next_action"] is True
    output_path = Path("data/negative_controls/false_closure_results_v0_2.json")
    save_false_closure_results(results, output_path)
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["pass"] is True
