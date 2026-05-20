import json
from pathlib import Path

from ai_objective_index.vnext_objective_router_audit import run_objective_router_claim_audit


def test_package_9c_docs_examples_and_outputs_exist():
    required = [
        "docs/vnext/package_9c_objective_router_api_mvp.md",
        "docs/vnext/objective_router_api.md",
        "docs/vnext/objective_router_mcp_tools.md",
        "docs/vnext/objective_router_response_standard.md",
        "docs/vnext/objective_router_limitations.md",
        "api/vnext/objective_router_openapi.json",
        "api/vnext/examples/objective_route_request.json",
        "api/vnext/examples/objective_route_response.json",
        "api/vnext/examples/capability_trust_request.json",
        "api/vnext/examples/capability_trust_response.json",
        "public_launch/wave5/OBJECTIVE_ROUTER_SAMPLE_RESPONSE.json",
        "public_launch/wave5/OBJECTIVE_ROUTER_MCP_TOOL_MANIFEST.json",
    ]
    for path in required:
        assert Path(path).exists(), path


def test_objective_router_claim_audit_passes():
    result = run_objective_router_claim_audit()
    assert result["overall_token"] == "PASS"
    assert result["risky_phrase_count"] == 0
    assert result["pypi_upload_performed"] is False
    assert result["mcp_registry_submission_performed"] is False
    payload = json.loads(Path("public_launch/wave5/OBJECTIVE_ROUTER_CLAIM_BOUNDARY_AUDIT.json").read_text())
    assert payload["token_printed"] is False
