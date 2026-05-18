from ai_objective_index.git_release_audit import (
    build_manual_upload_commands,
    run_git_release_audit,
    should_ignore_path,
)
from ai_objective_index.no_secrets_audit import SECRET_PATTERNS


def test_git_release_audit_ignore_helpers():
    assert should_ignore_path("__pycache__/module.pyc")
    assert should_ignore_path(".pytest_cache/v/cache/nodeids")
    assert should_ignore_path("pytest-cache-files-abc123")
    assert should_ignore_path(".env")
    assert should_ignore_path("data/source_cache/page.html")
    assert should_ignore_path("mcp_registry_raw_v0_1.json")
    assert should_ignore_path("SOURCE_0513_REPACK_FINAL_v1/03_CORE.md")
    assert not should_ignore_path("README.md")
    assert not should_ignore_path("data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json")


def test_git_release_audit_patterns_and_commands_are_safe():
    result = run_git_release_audit()
    commands = build_manual_upload_commands()
    secret_names = {name for name, _pattern in SECRET_PATTERNS}

    assert result["all_ignore_examples_covered"]
    assert "openai_key" in secret_names
    assert "gh auth login" in commands
    assert "token" not in commands.lower().replace("tokens", "")
    assert "--force" not in commands.lower()
