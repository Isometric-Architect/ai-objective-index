from ai_objective_index.portfolio.feedback_second_run_skipped import build_skipped_report


def test_skipped_report_for_hold_candidate():
    report = build_skipped_report(
        {
            "second_run_candidate_id": "candidate-qira",
            "reply_id": "reply-qira",
            "vertical": "qira",
            "readiness": "HOLD_NEEDS_ARTIFACT",
            "required_artifacts": ["redacted local artifact summary"],
        }
    )
    assert report.reason == "HOLD_NEEDS_ARTIFACT"
    assert report.can_retry_after_artifact is True
    assert report.reply_id == "reply-qira"
