from pathlib import Path

from ai_objective_index.qira.cli_demo import run_qira_cli_demo


def test_qira_cli_demo_writes_outputs():
    payload = run_qira_cli_demo()

    assert payload["decision_token"] == "PASS_CONTRACT_SCOPED"
    assert Path("public_launch/qira1/QIRA_1_RELEASEGATE_RESULT.json").exists()
    assert Path("public_launch/qira1/QIRA_SAMPLE_PATCH_RECEIPT.json").exists()
    assert Path("public_launch/qira1/QIRA_SAMPLE_ACTION_LICENSE.json").exists()
    assert Path("public_launch/qira1/QIRA_1_NEXT_STEPS.md").exists()
