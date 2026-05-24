from pathlib import Path


def test_qira1_docs_exist():
    for path in [
        "docs/qira_releasegate_mvp.md",
        "docs/qira_action_license.md",
        "docs/qira_claim_boundaries.md",
        "docs/qira_code_releasegate_plan.md",
    ]:
        assert Path(path).exists(), path


def test_qira1_public_outputs_exist():
    for path in [
        "public_launch/qira1/QIRA_1_RELEASEGATE_RESULT.json",
        "public_launch/qira1/QIRA_SAMPLE_CONTRACT.json",
        "public_launch/qira1/QIRA_SAMPLE_PATCH_RECEIPT.json",
        "public_launch/qira1/QIRA_SAMPLE_ACTION_LICENSE.json",
        "public_launch/qira1/QIRA_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/qira1/QIRA_1_NEXT_STEPS.md",
    ]:
        assert Path(path).exists(), path
