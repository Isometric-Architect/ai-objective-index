from ai_objective_index.vnext.objective_router_models import ObjectiveRouteRequest, ObjectiveRouteResponse, ObjectiveRouteSummary


def test_objective_route_request_defaults_validate():
    request = ObjectiveRouteRequest(query="browser automation", objective="select MCP candidates")
    assert request.domain == "mcp_servers"
    assert request.data_scope == "sample"
    assert request.constraints.require_source_trace is True
    assert request.include.source_traces is True


def test_objective_route_response_serializes():
    response = ObjectiveRouteResponse(
        query="q",
        objective="o",
        domain="mcp_servers",
        data_scope="sample",
        generated_at="2026-05-21T00:00:00Z",
        route_summary=ObjectiveRouteSummary(total_candidates=0),
        results=[],
    )
    payload = response.model_dump(mode="json", by_alias=True)
    assert payload["schema"] == "AOI_ObjectiveRouteResponse/v0.1"
    assert "verified" in payload["must_not_claim"]
    assert payload["probe_execution"] is False
