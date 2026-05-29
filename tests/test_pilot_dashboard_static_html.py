from pathlib import Path

from ai_objective_index.portfolio.pilot_dashboard_builder import generate_dashboard
from ai_objective_index.portfolio.roe16_dashboard_gate import html_has_external_dependency


def test_static_html_generated_without_external_dependency():
    generate_dashboard(write_result=True)
    html = Path("pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.html").read_text(encoding="utf-8")
    assert "Local/static artifact only" in html
    assert "<script" not in html.lower()
    assert "<link" not in html.lower()
    assert "<form" not in html.lower()
    assert html_has_external_dependency() is False
