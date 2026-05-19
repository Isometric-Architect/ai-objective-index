from pathlib import Path


def test_hf_upload_docs_and_commands_are_safe():
    assert Path("docs/package_8g_huggingface_private_upload.md").exists()
    assert Path("docs/huggingface_cli_upload.md").exists()
    assert Path("docs/huggingface_post_upload_checklist.md").exists()
    commands = Path("huggingface_upload/HF_UPLOAD_COMMANDS.md").read_text(encoding="utf-8")
    browser = Path("huggingface_upload/HF_BROWSER_FALLBACK_STEPS.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Do not paste Hugging Face tokens into ChatGPT/Codex chat" in commands
    assert "Visibility: **Private**" in browser
    assert "hf_auth_check" in readme
    assert "hf_private_upload --dry-run" in readme

