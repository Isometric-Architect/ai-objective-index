from ai_objective_index.agent_discovery_eval import (
    CAPABILITY_DECISION_PACKET_DRAFT_PATH,
    FRESHNESS_RUGPULL_NOTES_PATH,
    HOLD_TO_REPLAN_SPEC_PATH,
    ROUTE_SEMANTICS_ROADMAP_PATH,
    repo_root,
)
from ai_objective_index.agent_discovery_eval.route_semantics_roadmap import run_route_semantics_roadmap


def test_route_semantics_include_required_state_separations():
    result = run_route_semantics_roadmap(write_result=True)
    text = (repo_root() / ROUTE_SEMANTICS_ROADMAP_PATH).read_text(encoding="utf-8")

    assert "FOUND_ONLY" in result["route_classes"]
    assert "HOLD_RUGPULL_DIFF" in result["route_classes"]
    assert "ESCALATE_DATACAPSULE" in result["route_classes"]
    assert "FOUND != TRUSTED" in text
    assert "TRUSTED != AUTHORIZED" in text
    assert "AUTHORIZED != EXECUTABLE" in text


def test_capability_decision_packet_and_hold_loop_fields_exist():
    run_route_semantics_roadmap(write_result=True)
    packet_text = (repo_root() / CAPABILITY_DECISION_PACKET_DRAFT_PATH).read_text(encoding="utf-8")
    hold_text = (repo_root() / HOLD_TO_REPLAN_SPEC_PATH).read_text(encoding="utf-8")
    freshness_text = (repo_root() / FRESHNESS_RUGPULL_NOTES_PATH).read_text(encoding="utf-8")

    for field in ("objective", "capability_id", "route_reason_codes", "decision_timestamp", "recheck_policy"):
        assert field in packet_text
    assert "max_iterations" in hold_text
    assert "Do not auto-approve" in hold_text
    assert "Version changes require recheck" in freshness_text
