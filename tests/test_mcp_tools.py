import json

from ai_objective_index import mcp_tools


def _assert_json_serializable(payload):
    json.dumps(payload)


def test_search_objectives_returns_results_and_is_json_serializable():
    result = mcp_tools.search_objectives(
        query="cheap image generation API with commercial use terms",
        domain="ai_tools",
        constraints={"budget_max": 50, "commercial_use_required": True},
        limit=5,
    )

    assert result["read_only"] is True
    assert result["results"]
    assert "objective_score" in result["results"][0]
    _assert_json_serializable(result)


def test_compare_tools_compares_at_least_two_sample_tools():
    result = mcp_tools.compare_tools(
        tool_ids=["aoi-pixelforge-api", "aoi-motioncanvas-ai"],
        compare_fields=["pricing", "docs", "policies", "status"],
        query="commercial image generation",
    )

    assert result["read_only"] is True
    assert len(result["comparison_table"]) == 2
    assert result["score_summary"]
    _assert_json_serializable(result)


def test_explain_score_returns_score_and_rank_reason():
    result = mcp_tools.explain_score("aoi-pixelforge-api")

    assert result["read_only"] is True
    assert result["objective_score"] >= 0
    assert result["rank_reason"]
    assert result["source_trace_ids"] == ["trace-pixelforge-pricing"]
    _assert_json_serializable(result)


def test_get_source_trace_returns_traces():
    result = mcp_tools.get_source_trace("aoi-pixelforge-api", field="pricing")

    assert result["read_only"] is True
    assert len(result["traces"]) == 1
    assert result["traces"][0]["field"] == "pricing"
    _assert_json_serializable(result)


def test_list_missing_fields_returns_list():
    result = mcp_tools.list_missing_fields("aoi-pixelforge-api")

    assert result["read_only"] is True
    assert isinstance(result["missing_fields"], list)
    assert any(item["field"] == "refund_policy" for item in result["missing_fields"])
    _assert_json_serializable(result)


def test_generate_decision_receipt_returns_known_limits_and_source_trace_ids():
    result = mcp_tools.generate_decision_receipt(
        query="cheap image generation API with commercial use terms",
        selected_object_id="aoi-pixelforge-api",
        alternatives=["aoi-motioncanvas-ai"],
        constraints={"budget_max": 50},
    )

    receipt = result["decision_receipt"]
    assert result["read_only"] is True
    assert "v0.1 read-only benchmark output" in receipt["known_limits"]
    assert "not a quality guarantee" in receipt["known_limits"]
    assert "verify source traces before production use" in receipt["known_limits"]
    assert "no purchase, booking, payment, login, email, or contract execution" in receipt["known_limits"]
    assert receipt["source_trace_ids"] == ["trace-pixelforge-pricing"]
    _assert_json_serializable(result)


def test_rank_options_handles_unknown_option_conservatively():
    result = mcp_tools.rank_options(
        options=[
            {"name": "PixelForge API"},
            {"name": "Unknown Outside Tool", "url": "https://unknown.example.com"},
        ],
        objective="cheap image generation API with commercial use terms",
        constraints={"budget_max": 50},
        scoring_profile="commercial_use",
    )

    unknown = next(item for item in result["results"] if item["name"] == "Unknown Outside Tool")
    assert unknown["objective_score"] == 10.0
    assert "Option is not in the local sample index; score is incomplete." in unknown["warnings"]
    _assert_json_serializable(result)

