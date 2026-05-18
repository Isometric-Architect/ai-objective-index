from pathlib import Path

from ai_objective_index.mcp_smoke import run_smoke


def test_mcp_smoke_runs_and_writes_summary():
    result = run_smoke(write_result=True)

    assert result["read_only"] is True
    assert result["live_network_used"] is False
    assert result["pass"] is True
    assert result["search_result_count"] > 0
    assert result["forbidden_actions_exposed_as_tools"] == []
    assert "payment" in result["forbidden_actions"]
    assert Path(result["output_path"]).exists()
