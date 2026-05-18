from pathlib import Path


def test_github_staging_docs_exist_and_state_boundaries():
    staging = Path("docs/github_staging_upload.md")
    checklist = Path("docs/github_post_upload_checklist.md")

    assert staging.exists()
    assert checklist.exists()
    text = staging.read_text(encoding="utf-8").lower()
    post = checklist.read_text(encoding="utf-8").lower()
    assert "private by default" in text
    assert "no force push" in text
    assert "no tokens" in text
    assert "not security certified" in post or "not security certification" in post
