from ai_objective_index.mcp_registry_server_json_builder import build_server_json, namespace_is_valid, write_server_json


def test_mcp_registry_server_json_builder_creates_draft():
    payload = write_server_json()

    assert namespace_is_valid(payload["name"])
    assert payload["read_only"] is True
    assert payload["draft_not_submittable"] is True
    assert "production-ready" not in str(payload).lower()
