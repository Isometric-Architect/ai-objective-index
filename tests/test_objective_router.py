from copy import deepcopy

from ai_objective_index.vnext.objective_router import _apply_constraints, route_objective
from ai_objective_index.vnext.objective_router_models import ObjectiveRouteRequest


def _allow_card() -> dict:
    return {
        "name": "Candidate",
        "object_id": "candidate",
        "integration_type": "mcp_server",
        "evidence_summary": {
            "source_trace_count": 1,
            "policy_found": False,
            "docs_found": False,
            "pricing_found": False,
            "license_found": False,
            "repository_found": False,
        },
        "risk_boundary": {
            "risk_level": "unknown",
            "forbidden_actions_detected": [],
            "unsupported_claims_detected": [],
        },
        "missing_fields": ["privacy_policy", "docs_url", "pricing"],
        "route_decision": {
            "decision": "ALLOW_CANDIDATE",
            "reason": "baseline",
            "next_actions": [],
            "can_rank": True,
            "can_compare": True,
            "can_recommend_as_candidate": True,
            "must_not_claim": ["verified"],
        },
    }


def test_route_objective_returns_decision_counts():
    response = route_objective(
        ObjectiveRouteRequest(
            query="image API",
            objective="select source-traced API candidates",
            domain="ai_apis",
            data_scope="sample",
            limit=3,
        )
    )
    assert response.route_summary.total_candidates <= 3
    assert response.read_only is True
    assert response.probe_execution is False


def test_route_preserves_hold_policy_clarity_when_present():
    response = route_objective(
        ObjectiveRouteRequest(
            query="browser automation MCP server",
            objective="select source-traced MCP candidates",
            data_scope="public_beta_mcp",
            limit=5,
        )
    )
    decisions = {card["route_decision"]["decision"] for card in response.results}
    if response.results:
        assert "HOLD_POLICY_CLARITY" in decisions


def test_constraints_make_route_stricter_not_looser():
    card = _allow_card()
    constrained = _apply_constraints(
        deepcopy(card),
        ObjectiveRouteRequest(
            query="q",
            objective="o",
            constraints={"require_policy_clarity": True, "require_docs": True},
        ),
    )
    assert constrained["route_decision"]["decision"] in {"HOLD_POLICY_CLARITY", "HOLD_MISSING_FIELDS"}
    assert constrained["route_decision"]["can_recommend_as_candidate"] is False


def test_forbidden_action_boundary_produces_block():
    card = _allow_card()
    card["risk_boundary"]["forbidden_actions_detected"] = ["payment"]
    constrained = _apply_constraints(card, ObjectiveRouteRequest(query="q", objective="o"))
    assert constrained["route_decision"]["decision"] == "BLOCK_FORBIDDEN_ACTION"
