from ai_objective_index import deployment_link_sync as sync


def test_deployment_link_sync_updates_private_links():
    target = sync._repo_root() / "tests" / "__tmp_8h_link_sync.md"
    try:
        target.write_text("GitHub repo:\nHugging Face Space: TODO / HOLD\n", encoding="utf-8")

        result = sync.sync_deployment_links(files=[target], write_result=False)
        text = target.read_text(encoding="utf-8")

        assert result["public_claim_added"] is False
        assert sync.GITHUB_URL in text
        assert sync.HF_SPACE_URL in text
        assert "private" in text.lower()
        assert "public release is complete" not in text.lower()
    finally:
        if target.exists():
            target.unlink()
