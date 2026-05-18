from __future__ import annotations

from ai_objective_index.registry_intake.mcp_registry_eval import run_mcp_registry_eval, save_mcp_registry_eval
from ai_objective_index.registry_intake.mcp_registry_export import export_mcp_registry_intake


def test_mcp_registry_eval_runs_on_fixture_outputs() -> None:
    export_mcp_registry_intake(use_fixture=True, allow_network=False)
    result = run_mcp_registry_eval()

    assert result["query_count"] == 5
    assert result["fixture_only"] is True
    assert result["live_network_used"] is False

    path = save_mcp_registry_eval(result)
    assert path.exists()
