from ai_objective_index.action_boundary import check_action_boundary, forbidden_actions_v0_1


def test_read_rank_compare_allowed() -> None:
    assert check_action_boundary("READ")["decision"] == "ALLOW"
    assert check_action_boundary("RANK")["decision"] == "ALLOW"
    assert check_action_boundary("COMPARE")["decision"] == "ALLOW"


def test_external_actions_blocked() -> None:
    for action in ["payment", "booking", "login", "email", "purchase", "contract_signing"]:
        assert check_action_boundary(action)["decision"] == "BLOCK"
    forbidden = forbidden_actions_v0_1()
    assert "payment" in forbidden
    assert "booking" in forbidden
    assert "login" in forbidden
    assert "purchase" in forbidden
    assert "contract_signing" in forbidden
