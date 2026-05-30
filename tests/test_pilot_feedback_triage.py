from ai_objective_index.portfolio.pilot_feedback_triage import route_feedback_category, write_feedback_triage_taxonomy


def test_feedback_triage_routes_categories():
    assert route_feedback_category("security_claim_concern")["route_to"] == "agentsec"
    assert route_feedback_category("code_release_boundary_concern")["route_to"] == "qira"
    assert route_feedback_category("privacy_or_license_concern")["route_to"] == "datacapsule"
    assert route_feedback_category("unknown-category")["route_to"] == "portfolio"


def test_feedback_triage_taxonomy_written():
    payload = write_feedback_triage_taxonomy()
    assert payload["category_count"] >= 10
    assert payload["auto_issue_creation_performed"] is False
    assert payload["external_api_used"] is False
