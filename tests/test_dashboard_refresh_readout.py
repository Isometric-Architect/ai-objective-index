from ai_objective_index.portfolio.dashboard_refresh_delta import build_dashboard_refresh_delta, delta_to_jsonable
from ai_objective_index.portfolio.dashboard_refresh_feedback_memory import build_dashboard_refresh_feedback_memory_summary
from ai_objective_index.portfolio.dashboard_refresh_loader import load_dashboard_refresh_sources
from ai_objective_index.portfolio.dashboard_refresh_readout import build_dashboard_refresh_readout
from ai_objective_index.portfolio.dashboard_refresh_status_cards import build_dashboard_refresh_status_cards


def test_dashboard_refresh_readout_explains_skipped_and_stale_status():
    loaded = load_dashboard_refresh_sources()
    readout = build_dashboard_refresh_readout(
        delta_to_jsonable(build_dashboard_refresh_delta(loaded)),
        build_dashboard_refresh_status_cards(loaded),
        build_dashboard_refresh_feedback_memory_summary(loaded),
    )
    assert "Skipped candidates are not failures and not successes" in readout
    assert "external share pack" in readout
    assert "Not certification" in readout
