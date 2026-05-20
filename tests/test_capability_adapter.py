from ai_objective_index.seed_loader import load_sample_index, load_source_traces
from ai_objective_index.vnext.capability_adapter import (
    action_object_to_capability_card,
    objective_request_to_objective_card,
    search_capability_trust_cards,
)


def test_adapter_builds_capability_card_from_sample_object():
    obj = load_sample_index()[0]
    traces = [trace for trace in load_source_traces() if trace.object_id == obj.object_id]
    card = action_object_to_capability_card(obj, traces)
    assert card.capability_id == f"capability:{obj.object_id}"
    assert card.permission_scope == ["read_only_metadata_candidate"]


def test_objective_request_adapter_creates_card():
    card = objective_request_to_objective_card("browser automation", "select source-traced candidates")
    assert card.forbidden_actions
    assert card.claim_ceiling.endswith("not verified")


def test_public_beta_mcp_scope_does_not_crash():
    objective, cards, warnings = search_capability_trust_cards(
        query="browser automation MCP",
        objective="select source-traced MCP candidates",
        data_scope="public_beta_mcp",
        limit=3,
    )
    assert objective.objective_id
    assert isinstance(cards, list)
    assert isinstance(warnings, list)
