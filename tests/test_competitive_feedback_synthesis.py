from ai_objective_index.agent_discovery_eval import COMPETITIVE_SYNTHESIS_PATH, repo_root
from ai_objective_index.agent_discovery_eval.competitive_feedback_synthesis import run_competitive_feedback_synthesis
from ai_objective_index.agent_discovery_eval.cross_model_feedback_classifier import run_cross_model_feedback_classifier


def test_competitive_feedback_synthesis_generates_required_sections():
    run_cross_model_feedback_classifier(write_result=True)
    result = run_competitive_feedback_synthesis(write_result=True)
    text = (repo_root() / COMPETITIVE_SYNTHESIS_PATH).read_text(encoding="utf-8")

    assert result["recommended_next_package"].startswith("AOI-AGENT-DISCOVERY-5")
    assert "What All Models Agree On" in text
    assert "What Models Disagree On" in text
    assert "Roadmap Changes" in text
    assert "not a security certification" in text
    assert "not product readiness proof" in text
