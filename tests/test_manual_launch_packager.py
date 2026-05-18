from pathlib import Path

from ai_objective_index.manual_launch_packager import create_manual_launch_pack


def test_manual_launch_packager_creates_launch_workspace():
    result = create_manual_launch_pack()
    launch_dir = Path(result["launch_dir"])

    assert launch_dir.exists()
    for name in {
        "README_LAUNCH_STEPS.md",
        "GITHUB_RELEASE_DRAFT.md",
        "COMMUNITY_POST_DRAFTS.md",
        "FINAL_SAFETY_CHECKLIST.md",
        "LAUNCH_FILE_MANIFEST.json",
        "LAUNCH_CHECKSUMS.json",
    }:
        assert (launch_dir / name).exists()
    github_draft = (launch_dir / "GITHUB_RELEASE_DRAFT.md").read_text(encoding="utf-8").lower()
    community = (launch_dir / "COMMUNITY_POST_DRAFTS.md").read_text(encoding="utf-8").lower()
    assert "read-only" in github_draft
    assert "not a quality guarantee" in github_draft
    assert "please test/break" in community
    assert result["actual_publish_performed"] is False
