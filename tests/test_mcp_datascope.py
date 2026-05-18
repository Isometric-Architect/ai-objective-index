from ai_objective_index import mcp_tools


def test_mcp_search_datascope_sample_generated_integrated():
    sample = mcp_tools.search_objectives("api", data_scope="sample", limit=3)
    generated = mcp_tools.search_objectives("api", data_scope="generated", limit=3)
    integrated = mcp_tools.search_objectives("api", data_scope="integrated", limit=3)

    assert sample["data_scope"] == "sample"
    assert generated["data_scope"] == "generated"
    assert integrated["data_scope"] == "integrated"
    assert sample["read_only"] is True
    assert generated["read_only"] is True
    assert integrated["read_only"] is True
    assert generated["results"]
    assert len(integrated["results"]) >= len(generated["results"])


def test_mcp_default_remains_sample_and_forbidden_actions_remain():
    result = mcp_tools.search_objectives("api", limit=3)
    assert result["data_scope"] == "sample"
    assert "payment" in result["forbidden_actions"]
    assert "purchase" in result["forbidden_actions"]
