from pathlib import Path

from ai_objective_index.portfolio.datacapsule_pilot_packager import package_datacapsule_pilot
from ai_objective_index.portfolio.roe10_datacapsule_pilot_gate import run_roe10_gate


ROOT = Path(__file__).resolve().parents[1]


def test_roe10_docs_and_schemas_exist():
    for relative in [
        "docs/portfolio/roe10_first_datacapsule_pilot_receipt_packager.md",
        "docs/portfolio/datacapsule_pilot_receipt_workflow.md",
        "docs/portfolio/datacapsule_corpus_manifest.md",
        "docs/portfolio/datacapsule_source_rights.md",
        "docs/portfolio/datacapsule_privacy_risk.md",
        "docs/portfolio/datacapsule_eval_leakage.md",
        "docs/portfolio/datacapsule_use_boundary.md",
        "docs/portfolio/datacapsule_pilot_claim_boundaries.md",
        "docs/portfolio/datacapsule_feedback_memory.md",
        "schemas/portfolio/datacapsule_pilot_receipt.schema.json",
        "schemas/portfolio/datacapsule_corpus_manifest.schema.json",
        "schemas/portfolio/datacapsule_source_rights_summary.schema.json",
        "schemas/portfolio/datacapsule_privacy_risk_summary.schema.json",
        "schemas/portfolio/datacapsule_eval_leakage_summary.schema.json",
        "schemas/portfolio/datacapsule_use_boundary.schema.json",
        "schemas/portfolio/datacapsule_feedback_memory.schema.json",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe10_outputs_exist_after_generation():
    package_datacapsule_pilot(sample=True)
    run_roe10_gate(write_result=True)

    for relative in [
        "pilot_receipts/datacapsule/DATACAPSULE_PILOT_RECEIPT_SAMPLE.json",
        "pilot_receipts/datacapsule/DATACAPSULE_CORPUS_MANIFEST_SAMPLE.json",
        "pilot_receipts/datacapsule/DATACAPSULE_SOURCE_RIGHTS_SUMMARY_SAMPLE.json",
        "pilot_receipts/datacapsule/DATACAPSULE_PRIVACY_RISK_SUMMARY_SAMPLE.json",
        "pilot_receipts/datacapsule/DATACAPSULE_EVAL_LEAKAGE_SUMMARY_SAMPLE.json",
        "pilot_receipts/datacapsule/DATACAPSULE_USE_BOUNDARY_SAMPLE.json",
        "pilot_receipts/datacapsule/DATACAPSULE_REVIEWER_READOUT.md",
        "pilot_receipts/datacapsule/DATACAPSULE_PILOT_FEEDBACK_MEMORY_ENTRY.json",
        "pilot_receipts/datacapsule/DATACAPSULE_PILOT_REDACTION_REPORT.json",
        "pilot_receipts/datacapsule/DATACAPSULE_PILOT_KNOWN_LIMITS.md",
        "public_launch/roe10/ROE10_DATACAPSULE_PILOT_GATE_RESULT.json",
        "public_launch/roe10/ROE10_DATACAPSULE_PILOT_SUMMARY.md",
        "public_launch/roe10/ROE10_NEXT_ACTIONS.md",
    ]:
        assert (ROOT / relative).exists(), relative
