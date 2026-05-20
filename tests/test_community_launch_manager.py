from pathlib import Path

from ai_objective_index.community_launch_manager import run_community_launch_manager


class FakeApi:
    def whoami(self):
        return {"name": "edict-lab"}

    def create_discussion(self, **kwargs):
        return "https://huggingface.co/spaces/edict-lab/ai-objective-index-demo/discussions/1"


def test_community_launch_manager_dry_run_creates_drafts():
    result = run_community_launch_manager(execute_safe=False, write_result=True)

    assert Path("public_launch/wave1/COMMUNITY_FEEDBACK_POST_DRAFTS.md").exists()
    assert Path("public_launch/wave1/HUGGINGFACE_DISCUSSION_DRAFT.md").exists()
    assert Path("public_launch/wave1/GITHUB_DISCUSSION_DRAFT.md").exists()
    assert result["dry_run"] is True
    assert result["external_manual_posts_created"] is False


def test_community_launch_manager_execute_safe_mocked_hf_discussion():
    result = run_community_launch_manager(execute_safe=True, api=FakeApi(), write_result=False)

    assert result["hf_discussion_created"] is True
    assert result["github_discussion_created"] is False
    assert result["manual_post_required"] is True
    assert result["token_printed"] is False
