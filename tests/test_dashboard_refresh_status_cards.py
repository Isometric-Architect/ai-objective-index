from ai_objective_index.portfolio.dashboard_refresh_loader import load_dashboard_refresh_sources
from ai_objective_index.portfolio.dashboard_refresh_status_cards import build_dashboard_refresh_status_cards


def test_dashboard_refresh_status_cards_preserve_skipped_candidates():
    cards = build_dashboard_refresh_status_cards(load_dashboard_refresh_sources())
    by_vertical = {card["vertical"]: card for card in cards}
    assert set(by_vertical) == {"agentsec", "qira", "datacapsule", "portfolio"}
    assert by_vertical["agentsec"]["feedback_second_run_status"] == "executed"
    assert by_vertical["agentsec"]["memory_status"] == "incorporated"
    for vertical in ["qira", "datacapsule", "portfolio"]:
        assert by_vertical[vertical]["feedback_second_run_status"] == "skipped_missing_artifact"
        assert by_vertical[vertical]["memory_status"] == "skipped_missing_artifact"
        assert "success" not in by_vertical[vertical]["feedback_second_run_status"]
