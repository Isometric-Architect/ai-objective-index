from pathlib import Path

from ai_objective_index.private_reviewer_packager import create_private_reviewer_pack


def test_private_reviewer_packager_writes_invite_and_drafts():
    result = create_private_reviewer_pack()
    invite = Path(result["invite_path"])
    text = invite.read_text(encoding="utf-8").lower()

    assert invite.exists()
    assert "github" in text
    assert "hugging face" in text
    assert "not verified" in text
    assert "not security certified" in text
    assert result["actual_post_performed"] is False
