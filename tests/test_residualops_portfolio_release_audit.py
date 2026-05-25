from pathlib import Path

from ai_objective_index.residualops_portfolio_release_audit import run_portfolio_release_audit
from ai_objective_index.residualops_portfolio_release_kit import run_portfolio_release_kit


def test_roe3_release_audit_passes_current_outputs():
    run_portfolio_release_kit(write_result=True)
    result = run_portfolio_release_audit(write_result=True)

    assert result["decision"] == "PASS_ROE3_CLAIM_BOUNDARY"
    assert result["risky_phrase_count"] == 0
    assert result["external_actions_performed"] is False
    assert result["private_kernel_exposed"] is False


def test_roe3_release_audit_detects_overclaim(tmp_path: Path, monkeypatch):
    import ai_objective_index.residualops_portfolio_release_audit as audit

    path = tmp_path / "public_launch" / "roe3"
    path.mkdir(parents=True)
    (tmp_path / "README.md").write_text("This is a verified capability.\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

    monkeypatch.setattr(audit, "_repo_root", lambda: tmp_path)
    result = audit.run_portfolio_release_audit(write_result=False)

    assert result["decision"] == "BLOCK_ROE3_OVERCLAIM"
    assert result["risky_phrase_count"] == 1
