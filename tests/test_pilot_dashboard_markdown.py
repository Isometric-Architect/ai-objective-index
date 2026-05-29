from pathlib import Path

from ai_objective_index.portfolio.pilot_dashboard_builder import generate_dashboard


def test_dashboard_markdown_generated():
    generate_dashboard(write_result=True)
    text = Path("pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.md").read_text(encoding="utf-8")
    assert "ResidualOps Pilot Dashboard" in text
    assert "ALLOW/HOLD/BLOCK Matrix" in text
    assert "Not security certification" in text
