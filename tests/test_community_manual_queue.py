from pathlib import Path

from ai_objective_index.community_manual_queue import write_community_manual_queue


def test_community_manual_queue_is_conservative():
    result = write_community_manual_queue()
    text = Path("public_launch/wave2/COMMUNITY_MANUAL_POST_QUEUE.md").read_text(encoding="utf-8").lower()

    assert result["external_auto_post"] is False
    assert "not verified" in text
    assert "not security certified" in text
    assert "not a quality guarantee" in text
    assert "safe mcp servers" not in text
