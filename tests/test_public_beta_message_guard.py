from pathlib import Path

from ai_objective_index.public_beta_message_guard import audit_message_text, run_public_beta_message_guard


def test_public_beta_message_guard_blocks_overclaim_phrase():
    result = audit_message_text("These are the best MCP servers with guaranteed ranking.")

    assert result["findings"]
    assert {item["phrase"] for item in result["findings"]} >= {"best mcp servers", "guaranteed ranking"}


def test_public_beta_message_guard_allows_conservative_draft():
    text = (
        "This is a read-only source-traced objective-based ranking demo. "
        "It uses registry metadata candidates. Please test and break it. "
        "It is not verified, not security certified, and not a quality guarantee."
    )
    result = audit_message_text(text)

    assert result["findings"] == []
    assert result["allowed_mentions"]


def test_public_beta_message_guard_writes_json_for_file():
    path = Path("tests/__tmp_public_beta_message_guard.md")
    path.write_text(
        "Read-only registry metadata candidates. Please test and break it. "
        "Not verified and not a quality guarantee.",
        encoding="utf-8",
    )
    try:
        result = run_public_beta_message_guard(files=[path], write_result=True)
    finally:
        path.unlink(missing_ok=True)

    assert result["overall_token"] == "PASS"
    assert Path("public_launch/PUBLIC_BETA_MESSAGE_GUARD_RESULT.json").exists()
