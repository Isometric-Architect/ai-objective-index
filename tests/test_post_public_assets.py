from pathlib import Path

from ai_objective_index.public_observation_plan import create_public_observation_assets


def test_post_public_assets_exist():
    create_public_observation_assets()

    assert Path("docs/package_8l_post_public_stabilization.md").exists()
    assert Path("docs/post_public_observation.md").exists()
    assert Path("docs/issue_feedback_after_public.md").exists()
    assert Path("docs/token_revocation_public_stage.md").exists()
    assert Path("public_launch/COMMUNITY_POST_STILL_HOLD.md").exists()
    assert Path("public_launch/POST_PUBLIC_GO_NO_GO_NEXT.md").exists()
