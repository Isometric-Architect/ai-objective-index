from ai_objective_index.portfolio.qira_patch_classifier import SAMPLE_PATCH_DIFF, classify_qira_patch


def test_qira_patch_classifier_identifies_risk_flags():
    result = classify_qira_patch("task-1", patch_text=SAMPLE_PATCH_DIFF)

    assert result.files_changed_count == 3
    assert "release_config_change" in result.risk_flags
    assert result.classification_decision == "BLOCK_FORBIDDEN_ACTION"


def test_qira_patch_classifier_blocks_secret_path():
    result = classify_qira_patch("task-2", changed_files=[".env"])

    assert result.classification_decision == "BLOCK_SECRET_RISK"
    assert "auth_or_token_handling" in result.risk_flags
