import json
from pathlib import Path


def test_example_files_exist():
    expected = [
        "examples/python_client.py",
        "examples/javascript_client.js",
        "examples/claude_desktop_config_example.json",
        "examples/chatgpt_app_prompt_examples.md",
        "examples/llamaindex_integration.md",
        "examples/langchain_integration.md",
    ]
    for path in expected:
        assert Path(path).exists()


def test_claude_desktop_config_example_parses():
    payload = json.loads(Path("examples/claude_desktop_config_example.json").read_text(encoding="utf-8"))

    assert "mcpServers" in payload
    assert "ai-objective-index" in payload["mcpServers"]

