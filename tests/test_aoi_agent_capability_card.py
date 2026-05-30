from ai_objective_index.agent_adoption import MCP_NAME, VERSION
from ai_objective_index.agent_adoption.capability_card import build_capability_card, validate_capability_card


def test_capability_card_validates():
    card = build_capability_card()

    assert validate_capability_card(card) == []
    assert card["version"] == VERSION
    assert card["mcp_name"] == MCP_NAME
    assert "discover" in card["modes"]
    assert "preflight" in card["modes"]


def test_capability_card_is_agent_native_discovery_router():
    card = build_capability_card()

    assert card["type"] == "objective_to_capability_discovery_and_preuse_trust_router"
    assert "ordinary_ai_agent" in card["primary_users"]
    assert "finding source-traced MCP/tool/API candidates for a specific objective" in card["best_for"]
    assert "external action authorization" in card["not_for"]


def test_capability_card_lists_private_kernel_without_values():
    card = build_capability_card()
    joined = " ".join(card["private_kernel_not_disclosed"]).lower()

    assert "ranking weights" in joined
    assert "thresholds" in joined
    assert ":" not in joined
    assert "=" not in joined

