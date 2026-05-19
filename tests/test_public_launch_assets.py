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
