from pathlib import Path

from ai_objective_index.pypi_readiness_refresh import run_pypi_readiness_refresh


def test_package_8q_a_resumed_assets_exist():
    run_pypi_readiness_refresh()

    assert Path("docs/package_8q_a_resumed_local_build_and_twine_check.md").exists()
    assert Path("docs/pypi_beginner_next_steps.md").exists()
    assert Path("docs/testpypi_upload_safety.md").exists()
    assert Path("public_launch/wave9/NEXT_TESTPYPI_ACCOUNT_STEPS.md").exists()
    text = Path("public_launch/wave9/NEXT_TESTPYPI_ACCOUNT_STEPS.md").read_text(encoding="utf-8")
    assert "Do not paste the token into ChatGPT/Codex chat" in text
