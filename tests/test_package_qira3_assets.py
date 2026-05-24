from pathlib import Path


def test_qira3_docs_exist():
    for path in [
        "docs/qira3_patch_classification.md",
        "docs/qira_test_command_contract.md",
    ]:
        assert Path(path).exists(), path


def test_qira3_outputs_exist():
    for path in [
        "public_launch/qira3/QIRA3_SAMPLE_TASK_PACKET.json",
        "public_launch/qira3/QIRA3_RELEASE_GATE_REPORT.json",
        "public_launch/qira3/QIRA3_PATH_CLASSIFICATION_REPORT.json",
        "public_launch/qira3/QIRA3_TEST_COMMAND_CONTRACT.json",
        "public_launch/qira3/QIRA3_REVIEW_RESULT.json",
        "public_launch/qira3/QIRA3_NEXT_STEPS.md",
        "public_launch/qira3/QIRA_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path
