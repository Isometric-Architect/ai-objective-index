from ai_objective_index.portfolio.feedback_second_run_candidate_selector import (
    load_feedback_second_run_candidates,
    select_feedback_second_run_candidates,
)


def test_selector_selects_only_ready_candidate():
    candidates = load_feedback_second_run_candidates()
    report = select_feedback_second_run_candidates(candidates)
    assert report.ready_count == 1
    assert report.hold_count == 3
    assert report.block_count == 0
    assert report.selected_verticals == ["agentsec"]
    assert sorted(report.skipped_verticals) == ["datacapsule", "portfolio", "qira"]


def test_selector_blocks_external_action_candidate():
    candidates = [
        {
            "second_run_candidate_id": "candidate-unsafe",
            "vertical": "agentsec",
            "readiness": "READY_FOR_LOCAL_SECOND_RUN",
            "external_action_authorized": True,
        }
    ]
    report = select_feedback_second_run_candidates(candidates)
    assert report.ready_count == 0
    assert report.block_count == 1
    assert report.skipped_candidates[0]["readiness"] == "BLOCK_EXTERNAL_ACTION"
