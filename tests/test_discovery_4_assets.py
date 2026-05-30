from pathlib import Path

from ai_objective_index.agent_discovery_eval import repo_root
from ai_objective_index.agent_discovery_eval.competitive_feedback_synthesis import run_competitive_feedback_synthesis
from ai_objective_index.agent_discovery_eval.discovery_4_gate import run_discovery_4_gate


EXPECTED_ASSETS = [
    "agent_discovery_eval/manual_cross_model/GEMINI_FEEDBACK_PACKET.json",
    "agent_discovery_eval/manual_cross_model/GPT55_THINKING_FEEDBACK_PACKET.json",
    "agent_discovery_eval/manual_cross_model/CLAUDE_OPUS48_FEEDBACK_PACKET.json",
    "agent_discovery_eval/manual_cross_model/CROSS_MODEL_FEEDBACK_SUMMARY.json",
    "agent_discovery_eval/manual_cross_model/COMPETITIVE_FEEDBACK_SYNTHESIS.md",
    "agent_discovery_eval/manual_cross_model/ROUTE_SEMANTICS_ROADMAP.md",
    "agent_discovery_eval/manual_cross_model/HOLD_TO_REPLAN_LOOP_SPEC.md",
    "agent_discovery_eval/manual_cross_model/CAPABILITY_DECISION_PACKET_DRAFT.md",
    "agent_discovery_eval/manual_cross_model/AGENT_OPERATOR_DUAL_POSITIONING.md",
    "agent_discovery_eval/manual_cross_model/FRESHNESS_RUGPULL_NEGATIVE_CACHE_NOTES.md",
    "agent_discovery_eval/manual_cross_model/TEST_RESIDUAL_RECONCILIATION_RESULT.json",
    "agent_discovery_eval/manual_cross_model/AOI_AGENT_DISCOVERY_4_GATE_RESULT.json",
    "agent_discovery_eval/manual_cross_model/AOI_AGENT_DISCOVERY_4_SUMMARY.md",
    "agent_discovery_eval/manual_cross_model/AOI_AGENT_DISCOVERY_4_NEXT_ACTIONS.md",
    "docs/aoi_cross_model_feedback_intake.md",
    "docs/aoi_capability_decision_packet.md",
    "docs/aoi_route_semantics_hardening.md",
    "docs/aoi_hold_to_replan_loop.md",
    "docs/aoi_agent_operator_dual_positioning.md",
    "docs/aoi_freshness_rugpull_negative_cache.md",
    "docs/aoi_test_residual_reconciliation.md",
]


def test_discovery_4_assets_exist_after_generation():
    run_competitive_feedback_synthesis(write_result=True)
    run_discovery_4_gate(write_result=True)

    missing = [path for path in EXPECTED_ASSETS if not (repo_root() / Path(path)).exists()]
    assert not missing
