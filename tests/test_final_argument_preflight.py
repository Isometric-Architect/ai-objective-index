from ai_objective_index.agent_adoption.final_argument_preflight import preflight_arguments


def test_final_argument_preflight_blocks_secret_like_input():
    result = preflight_arguments("api.call", {"token": "sk-1234567890123456"})

    assert result["route_decision"] == "BLOCK_SECRET_OR_PRIVATE_DATA"
    assert result["reason_code"] == "SECRET_LIKE_INPUT"
    assert result["external_action_authorization"] is False


def test_final_argument_preflight_catches_dangerous_arguments():
    assert preflight_arguments("github.create_pr", {"release": True})["route_decision"] == "ESCALATE_QIRA"
    assert preflight_arguments("email.send", {"recipient": "external@example.invalid"})["route_decision"] == "ESCALATE_HUMAN_APPROVAL"
    assert preflight_arguments("database.query", {"sql": "DELETE FROM users"})["route_decision"] == "BLOCK_DESTRUCTIVE_ACTION"
    assert preflight_arguments("browser.submit_form", {"url": "local"})["route_decision"] == "ESCALATE_HUMAN_APPROVAL"
