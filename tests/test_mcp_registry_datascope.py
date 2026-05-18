from __future__ import annotations

from ai_objective_index import mcp_tools
from ai_objective_index.registry_intake.mcp_registry_export import export_mcp_registry_intake


def test_mcp_search_mcp_registry_scope_works() -> None:
    export_mcp_registry_intake(use_fixture=True, allow_network=False)

    result = mcp_tools.search_objectives("browser automation MCP", data_scope="mcp_registry", limit=5)

    assert result["read_only"] is True
    assert result["data_scope"] == "mcp_registry"
    assert result["results"]
    assert "payment" in result["forbidden_actions"]


def test_mcp_search_public_beta_mcp_warns_or_returns_results() -> None:
    export_mcp_registry_intake(use_fixture=True, allow_network=False)

    result = mcp_tools.search_objectives("browser automation MCP", data_scope="public_beta_mcp", limit=5)

    assert result["read_only"] is True
    assert result["data_scope"] == "public_beta_mcp"
    assert result["results"] or result["warnings"]
    assert "contract_signing" in result["forbidden_actions"]
