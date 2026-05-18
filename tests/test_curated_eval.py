from __future__ import annotations

from ai_objective_index.curated_eval import run_curated_eval


def test_curated_eval_runs_with_placeholder_warning() -> None:
    result = run_curated_eval()

    assert result["query_count"] > 0
    assert result["read_only"] is True
    assert result["live_network_used"] is False
    assert any("placeholder" in warning.lower() for warning in result["warnings"])
