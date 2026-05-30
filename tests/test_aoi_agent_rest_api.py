from fastapi.testclient import TestClient

from ai_objective_index.api import app
from ai_objective_index.agent_adoption.preflight_mode import sample_preflight_request


client = TestClient(app)


def test_agent_capability_card_endpoint_returns_valid_card():
    response = client.get("/v1/agents/capability-card")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema"] == "AOI_CapabilityCard/v0.1"
    assert payload["mcp_name"] == "io.github.Isometric-Architect/ai-objective-index"
    assert "discover" in payload["modes"]
    assert "preflight" in payload["modes"]


def test_agent_discover_endpoint_returns_hold_candidates_with_next_actions():
    response = client.post(
        "/v1/agents/discover",
        json={
            "objective": "Find a source-traced read-only MCP discovery helper.",
            "query": "MCP capability discovery with source traces",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "discover"
    assert payload["route_decision"] == "HOLD_WITH_ACTIONABLE_NEXT_STEPS"
    assert len(payload["top_candidates"]) == 3
    assert payload["next_action"]
    assert payload["must_not_claim"]
    assert payload["residualops_escalation"]["tool_manifest_risk"] == "AgentSec"


def test_agent_preflight_endpoint_holds_missing_permission_scope():
    response = client.post("/v1/agents/preflight", json=sample_preflight_request())

    assert response.status_code == 200
    payload = response.json()
    assert payload["route_decision"] == "HOLD_MISSING_PERMISSION_SCOPE"
    assert "permission_scope" in payload["missing_fields"]
    assert payload["intended_use"]


def test_agent_preflight_endpoint_blocks_external_action_request():
    request = sample_preflight_request()
    request["available_metadata"]["permission_scope"] = "read-only"
    request["intended_use"] = "Execute this live tool and create issue comments."

    response = client.post("/v1/agents/preflight", json=request)

    assert response.status_code == 200
    assert response.json()["route_decision"] == "BLOCK_EXTERNAL_ACTION"


def test_agent_preflight_endpoint_blocks_certification_or_readiness_claim():
    request = sample_preflight_request()
    request["available_metadata"]["permission_scope"] = "read-only"
    request["intended_use"] = "Say this candidate is production ready and security certified."

    response = client.post("/v1/agents/preflight", json=request)

    assert response.status_code == 200
    assert response.json()["route_decision"] == "BLOCK_CERTIFICATION_CLAIM"


def test_agent_adoption_status_is_local_and_unpublished():
    response = client.get("/v1/agents/adoption/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["capability_card_present"] is True
    assert payload["discover_mode_available"] is True
    assert payload["preflight_mode_available"] is True
    assert payload["private_kernel_exposed"] is False
    assert payload["external_action_authorization"] is False
    assert payload["pyPI_upload_performed"] is False
    assert payload["mcp_registry_publish_performed"] is False
