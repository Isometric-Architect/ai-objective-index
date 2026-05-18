from ai_objective_index import mcp_compat


def test_search_returns_results_and_read_only():
    result = mcp_compat.search("cheap image generation API", limit=3)

    assert result["read_only"] is True
    assert result["data_scope"] == "sample"
    assert result["results"]
    assert result["status"] == "ok"
    assert result["limitations"]
    assert "payment" in result["forbidden_actions"]


def test_fetch_returns_object_details_for_known_object():
    result = mcp_compat.fetch("aoi-pixelforge-api")

    assert result["read_only"] is True
    assert result["data_scope"] == "sample"
    assert result["object"]["object_id"] == "aoi-pixelforge-api"
    assert result["score"]["objective_score"] >= 0
    assert isinstance(result["source_traces"], list)
    assert isinstance(result["missing_fields"], list)


def test_fetch_unknown_object_returns_clear_error():
    result = mcp_compat.fetch("aoi-does-not-exist")

    assert result["read_only"] is True
    assert result["status"] == "not_found"
    assert result["error"] == "object_not_found"
    assert result["limitations"]


def test_search_fetch_integrated_scope_work():
    search_result = mcp_compat.search("image API", data_scope="integrated", limit=5)
    assert search_result["data_scope"] == "integrated"
    top_id = search_result["results"][0]["object_id"]
    fetch_result = mcp_compat.fetch(top_id, data_scope="integrated")
    assert fetch_result["data_scope"] == "integrated"
    assert fetch_result["read_only"] is True
