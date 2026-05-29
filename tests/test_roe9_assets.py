from pathlib import Path

from ai_objective_index.portfolio.qira_pilot_packager import package_qira_pilot
from ai_objective_index.portfolio.roe9_qira_pilot_gate import run_roe9_gate


ROOT = Path(__file__).resolve().parents[1]


def test_roe9_docs_and_schemas_exist():
    for relative in [
        "docs/portfolio/roe9_first_qira_pilot_receipt_packager.md",
        "docs/portfolio/qira_pilot_receipt_workflow.md",
        "docs/portfolio/qira_task_packet.md",
        "docs/portfolio/qira_patch_classification.md",
        "docs/portfolio/qira_behavior_contract.md",
        "docs/portfolio/qira_ci_evidence_summary.md",
        "docs/portfolio/qira_pilot_claim_boundaries.md",
        "docs/portfolio/qira_feedback_memory.md",
        "schemas/portfolio/qira_pilot_receipt.schema.json",
        "schemas/portfolio/qira_task_packet.schema.json",
        "schemas/portfolio/qira_patch_classification.schema.json",
        "schemas/portfolio/qira_behavior_contract.schema.json",
        "schemas/portfolio/qira_ci_evidence_summary.schema.json",
        "schemas/portfolio/qira_feedback_memory.schema.json",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe9_outputs_exist_after_generation():
    package_qira_pilot(sample=True)
    run_roe9_gate(write_result=True)

    for relative in [
        "pilot_receipts/qira/QIRA_PILOT_RECEIPT_SAMPLE.json",
        "pilot_receipts/qira/QIRA_TASK_PACKET_SAMPLE.json",
        "pilot_receipts/qira/QIRA_PATCH_CLASSIFICATION_SAMPLE.json",
        "pilot_receipts/qira/QIRA_BEHAVIOR_CONTRACT_SAMPLE.json",
        "pilot_receipts/qira/QIRA_CI_EVIDENCE_SUMMARY_SAMPLE.json",
        "pilot_receipts/qira/QIRA_REVIEWER_READOUT.md",
        "pilot_receipts/qira/QIRA_PILOT_FEEDBACK_MEMORY_ENTRY.json",
        "pilot_receipts/qira/QIRA_PILOT_REDACTION_REPORT.json",
        "pilot_receipts/qira/QIRA_PILOT_KNOWN_LIMITS.md",
        "public_launch/roe9/ROE9_QIRA_PILOT_GATE_RESULT.json",
        "public_launch/roe9/ROE9_QIRA_PILOT_SUMMARY.md",
        "public_launch/roe9/ROE9_NEXT_ACTIONS.md",
    ]:
        assert (ROOT / relative).exists(), relative
