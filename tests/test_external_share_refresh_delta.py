from ai_objective_index.portfolio.external_share_refresh_delta import build_external_share_refresh_delta, delta_to_jsonable
from ai_objective_index.portfolio.external_share_refresh_loader import load_external_share_refresh_sources


def test_external_share_refresh_delta_serializes_stale_to_refreshed():
    delta = delta_to_jsonable(build_external_share_refresh_delta(load_external_share_refresh_sources()))
    assert delta["schema"] == "ResidualOps_ExternalShareRefreshDelta/v0.1"
    assert delta["previous_share_pack_status"] == "stale"
    assert delta["new_share_pack_status"] == "refreshed_from_roe21"
    assert "qira_skipped_missing_artifact_visible" in delta["updates"]
    assert delta["no_external_action"] is True
