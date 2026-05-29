from pathlib import Path

from ai_objective_index.portfolio.agentsec_pilot_packager import package_agentsec_pilot
from ai_objective_index.portfolio.roe8_agentsec_pilot_gate import run_roe8_gate


ROOT = Path(__file__).resolve().parents[1]


def test_roe8_docs_and_schemas_exist():
    for relative in [
        "docs/portfolio/roe8_first_agentsec_pilot_receipt_packager.md",
        "docs/portfolio/agentsec_pilot_receipt_workflow.md",
        "docs/portfolio/agentsec_pilot_claim_boundaries.md",
        "docs/portfolio/agentsec_pilot_feedback_memory.md",
        "schemas/portfolio/agentsec_pilot_receipt.schema.json",
        "schemas/portfolio/agentsec_pilot_feedback_memory.schema.json",
        "schemas/portfolio/agentsec_pilot_readout.schema.json",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe8_outputs_exist_after_generation():
    package_agentsec_pilot(sample=True)
    run_roe8_gate(write_result=True)

    for relative in [
        "pilot_receipts/agentsec/AGENTSEC_PILOT_RECEIPT_SAMPLE.json",
        "pilot_receipts/agentsec/AGENTSEC_PILOT_REVIEWER_READOUT.md",
        "pilot_receipts/agentsec/AGENTSEC_PILOT_FEEDBACK_MEMORY_ENTRY.json",
        "pilot_receipts/agentsec/AGENTSEC_PILOT_REDACTION_REPORT.json",
        "pilot_receipts/agentsec/AGENTSEC_PILOT_KNOWN_LIMITS.md",
        "public_launch/roe8/ROE8_AGENTSEC_PILOT_GATE_RESULT.json",
        "public_launch/roe8/ROE8_AGENTSEC_PILOT_SUMMARY.md",
        "public_launch/roe8/ROE8_NEXT_ACTIONS.md",
    ]:
        assert (ROOT / relative).exists(), relative
