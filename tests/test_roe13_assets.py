from pathlib import Path

from ai_objective_index.real_pypi_upload_gate import _repo_root


def test_roe13_docs_and_assets_exist():
    expected = [
        "docs/portfolio/roe13_first_owner_consented_pilot_dry_run.md",
        "docs/portfolio/pilot_dry_run_workflow.md",
        "docs/portfolio/pilot_dry_run_receipt.md",
        "docs/portfolio/pilot_dry_run_claim_boundaries.md",
        "docs/portfolio/pilot_dry_run_feedback_memory.md",
        "docs/portfolio/pilot_dry_run_operator_checklist.md",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_RECEIPT.json",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_TRACE.json",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_RESULT_AGENTSEC.json",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_RESULT_QIRA.json",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_RESULT_DATACAPSULE.json",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_REVIEWER_READOUT.md",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_FEEDBACK_MEMORY.json",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_REDACTION_REPORT.json",
        "pilot_dry_runs/ROE13_PILOT_DRY_RUN_KNOWN_LIMITS.md",
        "public_launch/roe13/ROE13_PILOT_DRY_RUN_GATE_RESULT.json",
        "public_launch/roe13/ROE13_PILOT_DRY_RUN_SUMMARY.md",
        "public_launch/roe13/ROE13_NEXT_ACTIONS.md",
    ]
    missing = [path for path in expected if not (_repo_root() / Path(path)).exists()]
    assert missing == []
