from pathlib import Path

from ai_objective_index.vnext.objective_router_cli_demo import OUTPUT_PATH, RESULT_PATH, run_demo


def test_objective_router_cli_demo_writes_sample_response():
    payload = run_demo(
        query="image API",
        objective="select source-traced API candidates",
        data_scope="sample",
        domain="ai_apis",
        limit=2,
    )
    assert payload["route_summary"]["total_candidates"] <= 2
    assert Path(OUTPUT_PATH).exists()
    assert Path(RESULT_PATH).exists()
    result_text = Path(RESULT_PATH).read_text(encoding="utf-8")
    assert '"network_used": false' in result_text
    assert '"mcp_registry_submission_performed": false' in result_text
