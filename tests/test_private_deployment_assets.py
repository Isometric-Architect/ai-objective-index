from pathlib import Path

from ai_objective_index.deployment_link_sync import write_static_assets


def test_private_deployment_assets_exist_after_helper():
    written = write_static_assets()

    assert Path("docs/package_8h_private_deployment_sync.md").exists()
    assert Path("docs/private_deployment_review.md").exists()
    assert Path("docs/hf_github_link_policy.md").exists()
    assert Path("deployment/private_deployment_v0_2/POST_DEPLOYMENT_REVIEW_CHECKLIST.md").exists()
    assert Path("deployment/private_deployment_v0_2/TOKEN_REVOCATION_REMINDER.md").exists()
    text = Path("deployment/private_deployment_v0_2/TOKEN_REVOCATION_REMINDER.md").read_text(encoding="utf-8").lower()
    assert "do not paste" in text
    assert "token" in text
    assert written
