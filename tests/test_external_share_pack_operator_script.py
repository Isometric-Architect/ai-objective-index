from pathlib import Path

from ai_objective_index.portfolio.external_share_pack_operator_script import write_operator_scripts


def test_external_share_operator_scripts_created():
    write_operator_scripts()
    script = Path("external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_OPERATOR_SCRIPT.md").read_text(encoding="utf-8")
    assert "claim ceiling banner" in script
    assert "Do not say certified" in script
