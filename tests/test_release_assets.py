from pathlib import Path

from ai_objective_index.public_beta_packager import create_public_beta_pack


def test_release_docs_exist_and_pack_is_manual_only():
    for path in [
        "docs/public_beta_release_plan.md",
        "docs/manual_publish_checklist.md",
        "docs/release_claim_review.md",
        "docs/smoke_test_matrix.md",
        "docs/package_7b_public_beta_rc.md",
    ]:
        assert Path(path).exists()

    result = create_public_beta_pack()
    release_dir = Path(result["release_dir"])
    checklist = (release_dir / "MANUAL_PUBLISH_CHECKLIST.md").read_text(encoding="utf-8").lower()
    assert "manual publish" in checklist
    assert "does not publish automatically" in checklist
