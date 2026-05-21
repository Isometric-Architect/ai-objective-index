from pathlib import Path


def test_package_8q_c_alt_docs_and_notes_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "docs" / "package_8q_c_alt_real_pypi_direct_upload.md").exists()
    assert (root / "docs" / "real_pypi_direct_upload_safety.md").exists()
    assert (root / "docs" / "mcp_registry_after_pypi.md").exists()
    assert (root / "public_launch" / "wave10_real_pypi" / "PYPI_TOKEN_SAFETY_NOTE.md").exists()
    assert (root / "public_launch" / "wave10_real_pypi" / "VERSION_CONFLICT_RECOVERY_PLAN.md").exists()


def test_package_8q_c_alt_token_note_warns_not_to_paste():
    root = Path(__file__).resolve().parents[1]
    text = (root / "public_launch" / "wave10_real_pypi" / "PYPI_TOKEN_SAFETY_NOTE.md").read_text(encoding="utf-8")
    assert "Do not paste token into ChatGPT/Codex chat" in text
    assert ".pypirc" in text
