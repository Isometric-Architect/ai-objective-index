from pathlib import Path

from ai_objective_index.agent_adoption.agent_adoption_packager import package_agent_adoption
from ai_objective_index.agent_adoption.agent_surface_audit import run_agent_surface_audit
from ai_objective_index.mcp_manifest import save_mcp_tool_manifest
from ai_objective_index.openapi_export import export_openapi


def test_agent_surface_assets_exist_after_packaging():
    package_agent_adoption()
    export_openapi()
    save_mcp_tool_manifest()
    result = run_agent_surface_audit(write_result=True)

    assert result["decision"] == "PASS_AGENT_SURFACES_READY_FOR_030A2_UPLOAD"
    for path in [
        "api/vnext/examples/agent/capability_card_response.json",
        "api/vnext/examples/agent/adoption_status_response.json",
        "public_launch/aoi_agent_adoption/AOI_AGENT_REST_SURFACE_RESULT.json",
        "public_launch/aoi_agent_adoption/AOI_AGENT_MCP_SURFACE_RESULT.json",
        "public_launch/aoi_agent_adoption/AOI_AGENT_SURFACE_AUDIT_RESULT.json",
        "docs/aoi_agent_rest_api.md",
        "docs/aoi_agent_mcp_tools.md",
        "docs/aoi_agent_surface_contract.md",
    ]:
        assert Path(path).exists()


def test_agent_surface_audit_reports_missing_openapi_path(monkeypatch):
    monkeypatch.setattr(
        "ai_objective_index.agent_adoption.agent_surface_audit._openapi_paths",
        lambda: {},
    )

    result = run_agent_surface_audit(write_result=False)

    assert result["decision"] == "HOLD_ENDPOINT_WIRING_INCOMPLETE"
    assert "/v1/agents/discover" in result["missing_rest_paths"]
