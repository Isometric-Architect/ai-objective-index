from ai_objective_index.agent_adoption.preflight_mode import preflight_capability, sample_preflight_request


def test_preflight_holds_missing_permission_scope():
    response = preflight_capability(sample_preflight_request())

    assert response["route_decision"] == "HOLD_MISSING_PERMISSION_SCOPE"
    assert "permission_scope" in response["missing_fields"]
    assert response["next_action"]


def test_preflight_blocks_external_action_request():
    request = sample_preflight_request()
    request["available_metadata"]["permission_scope"] = "read-only"
    request["intended_use"] = "Execute the tool and create issue comments."

    response = preflight_capability(request)

    assert response["route_decision"] == "BLOCK_EXTERNAL_ACTION"
    assert response["external_action_performed"] is False


def test_preflight_blocks_certification_request():
    request = sample_preflight_request()
    request["available_metadata"]["permission_scope"] = "read-only"
    request["intended_use"] = "Say this candidate is security certified for users."

    response = preflight_capability(request)

    assert response["route_decision"] == "BLOCK_CERTIFICATION_CLAIM"


def test_preflight_blocks_secret_like_metadata():
    request = sample_preflight_request()
    request["available_metadata"]["permission_scope"] = "read-only"
    request["available_metadata"]["api_key"] = "sk-exampletoken123456"

    response = preflight_capability(request)

    assert response["route_decision"] == "BLOCK_SECRET_OR_PRIVATE_DATA"


def test_preflight_policy_clarity_hold_after_permission_scope():
    request = sample_preflight_request()
    request["available_metadata"]["permission_scope"] = "read-only"

    response = preflight_capability(request)

    assert response["route_decision"] == "HOLD_POLICY_CLARITY"
    assert "privacy_policy" in response["missing_fields"]
    assert "data_retention" in response["missing_fields"]

