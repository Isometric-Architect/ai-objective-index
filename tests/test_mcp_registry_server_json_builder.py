from ai_objective_index.mcp_registry_server_json_builder import build_server_json, namespace_is_valid, write_server_json


def test_mcp_registry_server_json_builder_creates_registry_ready_candidate():
    payload = write_server_json()

    assert namespace_is_valid(payload["name"])
    assert payload["$schema"].startswith("https://static.modelcontextprotocol.io/schemas/")
    assert payload["read_only"] is True
    assert payload["artifacts"]["python_package_artifact_exists"] is True
    assert payload["draft_not_submittable"] is False
    assert "production-ready" not in str(payload).lower()
