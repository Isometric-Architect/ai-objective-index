from ai_objective_index.portfolio.external_share_refresh_claim_audit import run_refresh_claim_audit


def test_external_share_refresh_claim_audit_blocks_overclaim(tmp_path):
    fixture = tmp_path / "overclaim.md"
    fixture.write_text("security certified\nproduction ready\n", encoding="utf-8")
    result = run_refresh_claim_audit([fixture], write_result=False)
    assert result["decision"] == "BLOCK_OVERCLAIM"
    assert result["risky_phrase_count"] == 2


def test_external_share_refresh_claim_audit_blocks_skipped_success(tmp_path):
    fixture = tmp_path / "skipped.md"
    fixture.write_text("skipped candidates succeeded\n", encoding="utf-8")
    result = run_refresh_claim_audit([fixture], write_result=False)
    assert result["decision"] == "BLOCK_OVERCLAIM"
    assert result["risky_phrase_count"] == 1
