from ai_objective_index.portfolio.feedback_second_run_candidate_selector import select_feedback_second_run_candidates, selection_report_to_jsonable
from ai_objective_index.portfolio.feedback_second_run_trace import build_bridge_trace


def test_bridge_trace_records_local_only_flags():
    selection = selection_report_to_jsonable(
        select_feedback_second_run_candidates(
            [
                {"second_run_candidate_id": "ready", "vertical": "agentsec", "readiness": "READY_FOR_LOCAL_SECOND_RUN"},
                {"second_run_candidate_id": "hold", "vertical": "qira", "readiness": "HOLD_NEEDS_ARTIFACT"},
            ]
        )
    )
    trace = build_bridge_trace(selection, [{"vertical": "agentsec"}], [{"vertical": "qira", "reason": "HOLD_NEEDS_ARTIFACT"}])
    assert trace.local_only is True
    assert trace.github_api_used is False
    assert trace.live_mcp_call_used is False
    assert trace.external_repo_modified is False
