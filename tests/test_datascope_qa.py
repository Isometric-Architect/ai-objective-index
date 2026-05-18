from ai_objective_index.datascope_qa import run_datascope_qa, save_datascope_qa_results
from ai_objective_index.registry_intake.mcp_registry_export import export_mcp_registry_intake


def test_datascope_qa_runs_and_includes_all_scopes():
    export_mcp_registry_intake(use_fixture=True, allow_network=False)
    results = run_datascope_qa()

    assert results["read_only"] is True
    assert results["live_network_used"] is False
    assert results["productization_mode"] is True
    assert set(results["scopes"]) == {
        "sample",
        "generated",
        "integrated",
        "curated",
        "public_beta",
        "mcp_registry",
        "public_beta_mcp",
    }
    assert results["scopes"]["generated"]["object_count"] >= 3
    assert results["scopes"]["curated"]["object_count"] >= 0
    assert results["scopes"]["public_beta"]["object_count"] >= 0
    assert results["scopes"]["mcp_registry"]["object_count"] >= 5
    assert results["scopes"]["public_beta_mcp"]["object_count"] >= 0
    assert results["scopes"]["generated"]["generated_unverified_status_ok"] is True
    assert results["summary"]["generated_objects_remain_extracted_unverified"] is True

    output = save_datascope_qa_results(results)
    assert output.exists()
