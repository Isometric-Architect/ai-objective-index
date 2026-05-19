from pathlib import Path

from ai_objective_index.prepublic_sync import write_prepublic_assets


def test_prepublic_assets_and_docs_exist():
    write_prepublic_assets()

    assert Path("public_launch/FINAL_PUBLIC_SWITCH_INSTRUCTIONS.md").exists()
    assert Path("public_launch/PREPUBLIC_REVIEW_CHECKLIST.md").exists()
    assert Path("docs/package_8j_prepublic_sync.md").exists()
    assert Path("docs/final_public_dry_run.md").exists()


def test_final_public_switch_instructions_are_manual_and_guarded():
    write_prepublic_assets()
    text = Path("public_launch/FINAL_PUBLIC_SWITCH_INSTRUCTIONS.md").read_text(encoding="utf-8").lower()

    assert "aoi_public_launch_confirm=yes" in text
    assert "does not make anything public" in text
    assert "do not claim verified" in text
