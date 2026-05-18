from __future__ import annotations

from ai_objective_index import mcp_tools
from ai_objective_index.registry_intake.registry_beta_dataset_builder import build_registry_beta_dataset


def test_mcp_public_beta_mcp_search_has_candidate_boundaries() -> None:
    build_registry_beta_dataset()

    result = mcp_tools.search_objectives("browser automation MCP", data_scope="public_beta_mcp", limit=5)

    assert result["read_only"] is True
    assert result["data_scope"] == "public_beta_mcp"
    assert result["results"] or result["warnings"]
    assert result["not_verified"] is True
    assert result["not_security_certified"] is True
    assert result["not_quality_guarantee"] is True
    assert "contract_signing" in result["forbidden_actions"]
