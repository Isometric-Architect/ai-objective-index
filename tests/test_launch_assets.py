from pathlib import Path

from ai_objective_index.manual_launch_packager import create_manual_launch_pack


def test_launch_docs_and_assets_exist():
    create_manual_launch_pack()
    root = Path.cwd()
    assert (root / "docs/package_8b_manual_public_beta_launch.md").exists()
    assert (root / "docs/manual_launch_execution.md").exists()
    assert (root / "docs/no_secrets_policy.md").exists()
    assert (root / "docs/launch_claim_guard.md").exists()
    checklist = (root / "launch/manual_public_beta_v0_2/FINAL_SAFETY_CHECKLIST.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "no publish performed" in checklist
    assert "no payment" in checklist
    assert "no live crawling" in checklist
