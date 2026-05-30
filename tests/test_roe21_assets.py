from pathlib import Path

from ai_objective_index.portfolio.dashboard_refresh_from_feedback import refresh_dashboard_from_feedback
from ai_objective_index.portfolio.roe21_dashboard_refresh_gate import run_roe21_gate


def test_roe21_assets_exist():
    refresh_dashboard_from_feedback(write_result=True)
    result = run_roe21_gate(write_result=True, ensure_refresh=False)
    assert result["decision"] == "PASS_DASHBOARD_REFRESHED_FROM_FEEDBACK_SECOND_RUN"
    required = [
        "docs/portfolio/roe21_dashboard_refresh_from_feedback_second_run.md",
        "docs/portfolio/dashboard_refresh_workflow.md",
        "docs/portfolio/dashboard_refresh_delta.md",
        "docs/portfolio/dashboard_refresh_claim_boundaries.md",
        "docs/portfolio/dashboard_refresh_operator_checklist.md",
        "docs/portfolio/external_share_pack_staleness_policy.md",
        "schemas/portfolio/dashboard_refresh_delta.schema.json",
        "schemas/portfolio/dashboard_refresh_status_card.schema.json",
        "schemas/portfolio/dashboard_refresh_gate.schema.json",
        "schemas/portfolio/dashboard_refresh_feedback_summary.schema.json",
        "pilot_dashboard/ROE21_DASHBOARD_REFRESH_DELTA.json",
        "pilot_dashboard/ROE21_FEEDBACK_SECOND_RUN_STATUS_CARDS.json",
        "pilot_dashboard/ROE21_FEEDBACK_SECOND_RUN_TIMELINE.json",
        "pilot_dashboard/ROE21_FEEDBACK_SECOND_RUN_MEMORY_SUMMARY.json",
        "pilot_dashboard/ROE21_DASHBOARD_REFRESH_READOUT.md",
        "pilot_dashboard/ROE21_DASHBOARD_REFRESH_REDACTION_REPORT.json",
        "pilot_dashboard/ROE21_DASHBOARD_REFRESH_CLAIM_AUDIT.json",
        "pilot_dashboard/ROE21_EXTERNAL_SHARE_PACK_STALE_NOTICE.md",
        "public_launch/roe21/ROE21_DASHBOARD_REFRESH_GATE_RESULT.json",
        "public_launch/roe21/ROE21_DASHBOARD_REFRESH_SUMMARY.md",
        "public_launch/roe21/ROE21_NEXT_ACTIONS.md",
    ]
    for path in required:
        assert Path(path).exists(), path
