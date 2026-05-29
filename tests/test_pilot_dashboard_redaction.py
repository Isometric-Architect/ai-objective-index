from ai_objective_index.portfolio.pilot_dashboard_builder import generate_dashboard
from ai_objective_index.portfolio.pilot_dashboard_redaction import scan_dashboard_payload


def test_dashboard_redaction_passes_current_artifacts():
    result = generate_dashboard(write_result=True)
    assert result["redaction"]["decision"] == "PASS_REDACTED"


def test_dashboard_redaction_blocks_token_like_string():
    result = scan_dashboard_payload("pypi-" + "a" * 24)
    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"
