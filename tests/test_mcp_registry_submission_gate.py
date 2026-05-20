from ai_objective_index.mcp_registry_submission_gate import evaluate_mcp_registry_eligibility, run_mcp_registry_submission_gate


def test_mcp_registry_submission_gate_holds_without_publishable_artifact():
    result = run_mcp_registry_submission_gate(execute=False, write_result=True, mcp_publisher_available=False)

    assert result["eligibility"]["decision"].startswith("HOLD")
    assert result["submission"]["submission_performed"] is False


def test_mcp_registry_submission_gate_invalid_namespace_blocks():
    eligibility = evaluate_mcp_registry_eligibility({"name": "Bad/Name"}, mcp_publisher_available=True)

    assert eligibility["decision"] == "BLOCK_INVALID_NAMESPACE"


def test_mcp_registry_submission_gate_execute_requires_env():
    result = run_mcp_registry_submission_gate(execute=True, env={}, write_result=False, mcp_publisher_available=True)

    assert result["submission"]["submission_performed"] is False
    assert result["submission"]["errors"]


def test_mcp_registry_submission_gate_pass_mocked_submit():
    server_json = {
        "name": "io.github.isometric-architect/ai-objective-index",
        "draft_not_submittable": False,
        "entrypoints": {"stdio_entrypoint_exists": True},
        "artifacts": {"python_package_artifact_exists": True, "remote_mcp_endpoint_exists": False},
    }
    eligibility = evaluate_mcp_registry_eligibility(server_json, mcp_publisher_available=True)
    assert eligibility["decision"] == "PASS_SUBMIT_READY"
