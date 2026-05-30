from ai_objective_index.agent_discovery_eval.mcp_registry_public_smoke import run_mcp_registry_public_smoke


def test_mcp_registry_public_smoke_passes_with_expected_body():
    body = "io.github.Isometric-Architect/ai-objective-index ai-objective-index 0.3.0a2 pypi"
    result = run_mcp_registry_public_smoke(
        fetcher=lambda: {"checked": True, "status_code": 200, "body": body},
        write_result=False,
    )

    assert result["decision"] == "PASS_MCP_REGISTRY_PUBLIC_SMOKE"
    assert result["matches"]["server_name"] is True


def test_mcp_registry_public_smoke_holds_when_unavailable():
    result = run_mcp_registry_public_smoke(
        fetcher=lambda: {"checked": False, "status_code": None, "body": "", "error": "offline"},
        write_result=False,
    )

    assert result["decision"] == "HOLD_REGISTRY_PROPAGATION"
