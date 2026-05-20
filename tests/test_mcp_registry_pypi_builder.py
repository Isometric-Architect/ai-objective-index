from ai_objective_index.mcp_registry_pypi_builder import build_pypi_server_json, write_pypi_server_json


def test_mcp_registry_pypi_builder_creates_registry_type_pypi():
    result = write_pypi_server_json()
    payload = build_pypi_server_json()

    assert result["name"] == "io.github.isometric-architect/ai-objective-index"
    assert result["registry_type"] == "pypi"
    assert payload["packages"][0]["registryType"] == "pypi"
    assert "not security certified" in " ".join(payload["limitations"])
    assert "production-ready" not in str(payload).lower()
