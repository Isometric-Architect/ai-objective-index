from ai_objective_index.portfolio.dashboard_refresh_claim_audit import run_dashboard_refresh_claim_audit


def test_dashboard_refresh_claim_audit_blocks_skipped_success_overclaim(tmp_path):
    fixture = tmp_path / "overclaim.md"
    fixture.write_text("skipped candidates succeeded\n", encoding="utf-8")
    result = run_dashboard_refresh_claim_audit([fixture], write_result=False)
    assert result["decision"] == "BLOCK_OVERCLAIM"
    assert result["risky_phrase_count"] == 1
