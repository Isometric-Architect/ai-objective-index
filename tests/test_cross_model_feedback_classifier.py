from ai_objective_index.agent_discovery_eval.cross_model_feedback_classifier import run_cross_model_feedback_classifier
from ai_objective_index.agent_discovery_eval.manual_cross_model_intake import run_manual_cross_model_intake


def test_cross_model_feedback_classifier_assigns_expected_categories():
    run_manual_cross_model_intake(write_result=True)
    summary = run_cross_model_feedback_classifier(write_result=True)

    assert summary["packet_count"] == 3
    assert "HOLD_TO_REPLAN_LOOP" in summary["categories_by_model"]["Gemini"]
    assert "ADAPTIVE_GOVERNANCE" in summary["categories_by_model"]["Gemini"]
    assert "CONTEXT_AWARE_POLICY" in summary["categories_by_model"]["Gemini"]
    assert "CAPABILITY_DECISION_PACKET" in summary["categories_by_model"]["GPT-5.5 Thinking"]
    assert "ROUTE_LABEL_GRANULARITY" in summary["categories_by_model"]["GPT-5.5 Thinking"]
    assert "TRUST_ROUTER_TRUST_REGRESSION" in summary["categories_by_model"]["Claude Opus 4.8 High"]
    assert "RUGPULL_DIFF" in summary["categories_by_model"]["Claude Opus 4.8 High"]
    assert "INCUMBENT_COMPETITION" in summary["categories_by_model"]["Claude Opus 4.8 High"]
    assert "AGENT_OPERATOR_POSITIONING" in summary["categories_by_model"]["Claude Opus 4.8 High"]


def test_cross_model_feedback_classifier_extracts_consensus_and_next_package():
    summary = run_cross_model_feedback_classifier(write_result=False)

    assert summary["all_models_direction_useful"] is True
    assert summary["simple_registry_insufficient"] is True
    assert summary["route_preflight_governance_model_count"] >= 2
    assert summary["adoption_friction_or_latency_model_count"] >= 2
    assert summary["recommended_next_package"].startswith("AOI-AGENT-DISCOVERY-5")
