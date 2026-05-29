from pathlib import Path

from ai_objective_index.portfolio.agentsec_pilot_packager import (
    FEEDBACK_MEMORY_PATH,
    RECEIPT_PATH,
    REDACTION_REPORT_PATH,
    REVIEWER_READOUT_PATH,
    package_agentsec_pilot,
)


def test_agentsec_pilot_packager_creates_sample_bundle():
    result = package_agentsec_pilot(sample=True)

    assert result["redaction"]["decision"] == "PASS_REDACTED"
    assert result["receipt"]["review_scope"]["live_tool_execution"] is False
    assert result["receipt"]["github_api_used"] is False
    assert Path(RECEIPT_PATH).exists()
    assert Path(REVIEWER_READOUT_PATH).exists()
    assert Path(REDACTION_REPORT_PATH).exists()
    assert Path(FEEDBACK_MEMORY_PATH).exists()


def test_agentsec_pilot_packager_uses_no_external_actions():
    result = package_agentsec_pilot(sample=True)

    assert result["external_actions_performed"] is False
    assert result["live_mcp_called"] is False
    assert result["external_tool_executed"] is False
    assert result["github_api_used"] is False
    assert result["token_printed"] is False
