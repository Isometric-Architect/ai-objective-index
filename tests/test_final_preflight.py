from ai_objective_index.final_preflight import run_final_preflight, save_final_preflight


def test_final_preflight_runs_and_stays_local():
    result = run_final_preflight()
    path = save_final_preflight(result)

    assert path.exists()
    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["actual_publish_performed"] is False
    assert result["live_network_used_in_preflight"] is False
    assert result["read_only"] is True
    assert result["counts"]["public_beta_mcp_count"] >= 0
    if result["counts"]["public_beta_mcp_count"] > 0:
        assert result["checks"]["real_registry_data"]["token"] == "PASS"
