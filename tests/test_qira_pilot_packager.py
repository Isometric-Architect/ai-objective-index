from pathlib import Path

from ai_objective_index.portfolio.qira_pilot_packager import RECEIPT_PATH, package_qira_pilot


def test_qira_pilot_packager_creates_artifacts():
    result = package_qira_pilot(sample=True)

    assert result["redaction"]["decision"] == "PASS_REDACTED"
    assert result["receipt"]["decision_summary"]["block_count"] == 1
    for path in result["paths"].values():
        assert Path(path).exists(), path


def test_qira_pilot_packager_does_not_use_external_actions():
    result = package_qira_pilot(sample=True)

    assert Path(RECEIPT_PATH).exists()
    assert result["github_api_used"] is False
    assert result["external_repo_modified"] is False
    assert result["merge_performed"] is False
    assert result["deploy_performed"] is False
