from pathlib import Path

from ai_objective_index.portfolio.feedback_second_run_executor import run_feedback_second_run_bridge
from ai_objective_index.portfolio.roe20_feedback_second_run_bridge_gate import run_roe20_gate


def test_roe20_docs_and_outputs_exist():
    run_feedback_second_run_bridge(sample=True, write_result=True)
    run_roe20_gate(write_result=True, ensure_bridge=True)
    expected = [
        "docs/portfolio/roe20_feedback_to_second_run_execution_bridge.md",
        "docs/portfolio/feedback_second_run_bridge_workflow.md",
        "docs/portfolio/feedback_second_run_candidate_selection.md",
        "docs/portfolio/feedback_second_run_skipped_candidates.md",
        "docs/portfolio/feedback_second_run_claim_boundaries.md",
        "docs/portfolio/feedback_second_run_operator_checklist.md",
        "schemas/portfolio/feedback_second_run_bridge_trace.schema.json",
        "schemas/portfolio/feedback_second_run_selection_report.schema.json",
        "schemas/portfolio/feedback_second_run_receipt.schema.json",
        "schemas/portfolio/feedback_second_run_skipped_report.schema.json",
        "schemas/portfolio/feedback_second_run_memory_update.schema.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_SELECTION_REPORT.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_TRACE.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_RECEIPT.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_RESULT_AGENTSEC.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_SKIPPED_QIRA.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_SKIPPED_DATACAPSULE.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_SKIPPED_PORTFOLIO.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_MEMORY_UPDATE.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_REVIEWER_READOUT.md",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_REDACTION_REPORT.json",
        "feedback_second_runs/ROE20_FEEDBACK_SECOND_RUN_KNOWN_LIMITS.md",
        "public_launch/roe20/ROE20_FEEDBACK_SECOND_RUN_BRIDGE_GATE_RESULT.json",
        "public_launch/roe20/ROE20_FEEDBACK_SECOND_RUN_BRIDGE_SUMMARY.md",
        "public_launch/roe20/ROE20_NEXT_ACTIONS.md",
    ]
    for path in expected:
        assert Path(path).exists(), path
