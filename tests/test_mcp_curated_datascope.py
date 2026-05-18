from __future__ import annotations

from ai_objective_index import mcp_tools


def test_mcp_search_curated_scope_works() -> None:
    result = mcp_tools.search_objectives("api", data_scope="curated", limit=5)

    assert result["read_only"] is True
    assert result["data_scope"] == "curated"
    assert "payment" in result["forbidden_actions"]


def test_mcp_search_public_beta_scope_warns_or_returns_results() -> None:
    result = mcp_tools.search_objectives("api", data_scope="public_beta", limit=5)

    assert result["read_only"] is True
    assert result["data_scope"] == "public_beta"
    assert result["results"] or result["warnings"]
    assert "contract_signing" in result["forbidden_actions"]
