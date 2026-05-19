from pathlib import Path

from ai_objective_index.no_contact_launch_gate import write_no_contact_launch_assets


def test_no_contact_public_beta_assets_exist():
    write_no_contact_launch_assets()

    assert Path("docs/no_contact_public_beta_strategy.md").exists()
    assert Path("docs/ai_reviewer_simulation.md").exists()
    assert Path("docs/issue_based_feedback_loop.md").exists()
    assert Path("public_launch/PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md").exists()
    assert Path("public_launch/NO_CONTACT_GO_NO_GO_DECISION.md").exists()


def test_no_contact_public_beta_draft_has_boundaries():
    write_no_contact_launch_assets()
    text = Path("public_launch/PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md").read_text(encoding="utf-8").lower()

    assert "read-only" in text
    assert "not verified" in text
    assert "not security certified" in text
    assert "not a quality guarantee" in text
    assert "github issues" in text
