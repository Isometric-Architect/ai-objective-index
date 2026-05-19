from pathlib import Path

from ai_objective_index.private_reviewer_packager import create_private_reviewer_pack
from ai_objective_index.public_launch_gate import write_public_launch_assets
from ai_objective_index.token_revocation_checklist import write_token_revocation_checklist


def test_public_launch_assets_exist():
    write_public_launch_assets()
    create_private_reviewer_pack()
    write_token_revocation_checklist()

    assert Path("docs/package_8i_public_launch_decision_gate.md").exists()
    assert Path("docs/public_launch_policy.md").exists()
    assert Path("docs/private_reviewer_workflow.md").exists()
    assert Path("docs/token_revocation_after_upload.md").exists()
    assert Path("public_launch/GO_NO_GO_DECISION.md").exists()
    assert Path("public_launch/PUBLIC_ANNOUNCEMENT_DRAFTS.md").exists()


def test_package_8k_public_launch_assets_exist():
    from ai_objective_index.public_launch_execute import write_post_public_assets

    write_post_public_assets()

    assert Path("docs/package_8k_public_visibility_switch.md").exists()
    assert Path("docs/post_public_review.md").exists()
    assert Path("public_launch/POST_PUBLIC_REVIEW_CHECKLIST.md").exists()
    assert Path("public_launch/COMMUNITY_POST_HOLD_NOTE.md").exists()
    assert Path("public_launch/TOKEN_REVOKE_AFTER_PUBLIC_NOTE.md").exists()

    token_note = Path("public_launch/TOKEN_REVOKE_AFTER_PUBLIC_NOTE.md").read_text(encoding="utf-8").lower()
    assert "do not paste tokens into chat" in token_note
