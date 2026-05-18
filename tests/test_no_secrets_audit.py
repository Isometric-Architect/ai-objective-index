from pathlib import Path

from ai_objective_index.no_secrets_audit import run_no_secrets_audit, save_no_secrets_audit


def test_no_secrets_audit_detects_real_looking_token():
    test_dir = Path("data/generated/test_no_secrets_audit")
    test_dir.mkdir(parents=True, exist_ok=True)
    secret_file = test_dir / "bad.md"
    secret_file.write_text("token: sk-thisLooksLikeARealSecret123456\n", encoding="utf-8")

    result = run_no_secrets_audit([secret_file])

    assert result["overall_token"] == "BLOCK"
    assert result["finding_count"] == 1


def test_no_secrets_audit_allows_redacted_placeholder():
    test_dir = Path("data/generated/test_no_secrets_audit")
    test_dir.mkdir(parents=True, exist_ok=True)
    placeholder = test_dir / "placeholder.md"
    placeholder.write_text("token: sk-REDACTED_EXAMPLE_PLACEHOLDER\n", encoding="utf-8")

    result = run_no_secrets_audit([placeholder])
    path = save_no_secrets_audit(result)

    assert path.exists()
    assert result["finding_count"] == 0
    assert result["warning_count"] == 1
    assert result["overall_token"] == "HOLD"
