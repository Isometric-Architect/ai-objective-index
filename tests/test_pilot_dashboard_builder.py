from pathlib import Path

from ai_objective_index.portfolio.pilot_dashboard_builder import build_dashboard, generate_dashboard
from ai_objective_index.portfolio.pilot_dashboard_loader import load_dashboard_sources


def test_dashboard_builder_aggregate_counts_match_second_run():
    result = generate_dashboard(write_result=True)
    counts = result["dashboard"]["aggregate_counts"]
    assert counts["second_run_allow"] == 3
    assert counts["second_run_hold"] == 3
    assert counts["second_run_block"] == 3
    assert counts["external_action_count"] == 0


def test_dashboard_builder_status_cards_include_three_verticals():
    dashboard = build_dashboard(load_dashboard_sources())
    verticals = {card["vertical"] for card in dashboard["vertical_status_cards"]}
    assert verticals == {"agentsec", "qira", "datacapsule"}
    assert Path("pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.json").exists()
