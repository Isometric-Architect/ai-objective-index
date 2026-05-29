from pathlib import Path


def test_roe15_docs_and_assets_exist():
    expected = [
        "docs/portfolio/roe15_local_owner_consented_second_run_receipt_packager.md",
        "docs/portfolio/second_run_receipt_workflow.md",
        "docs/portfolio/second_run_delta.md",
        "docs/portfolio/second_run_feedback_memory.md",
        "docs/portfolio/second_run_claim_boundaries.md",
        "docs/portfolio/second_run_operator_checklist.md",
        "schemas/portfolio/second_run_receipt.schema.json",
        "schemas/portfolio/second_run_delta.schema.json",
        "schemas/portfolio/second_run_feedback_memory.schema.json",
        "schemas/portfolio/second_run_artifact_index.schema.json",
    ]
    for path in expected:
        assert Path(path).exists(), path
