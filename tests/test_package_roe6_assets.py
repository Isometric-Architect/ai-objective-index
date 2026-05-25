from pathlib import Path

from ai_objective_index.residualops_pilot_feedback_memory import run_pilot_feedback_memory


ROOT = Path(__file__).resolve().parents[1]


def test_roe6_docs_exist():
    for relative in [
        "docs/roe6_pilot_feedback_memory.md",
        "docs/residualops_pilot_receipt_intake.md",
        "docs/residualops_feedback_memory_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe6_outputs_exist_after_generation():
    run_pilot_feedback_memory(write_result=True)

    for relative in [
        "public_launch/roe6/ROE6_PILOT_FEEDBACK_MEMORY_RESULT.json",
        "public_launch/roe6/ROE6_PILOT_RECEIPT_TEMPLATE.json",
        "public_launch/roe6/ROE6_RECEIPT_INTAKE_GATE.json",
        "public_launch/roe6/ROE6_PILOT_FEEDBACK_MEMORY.json",
        "public_launch/roe6/ROE6_PILOT_OUTCOME_SUMMARY.md",
        "public_launch/roe6/ROE6_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/roe6/ROE6_ARTIFACT_MANIFEST.json",
        "public_launch/roe6/ROE6_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe6_summary_is_public_safe():
    run_pilot_feedback_memory(write_result=True)
    text = (ROOT / "public_launch/roe6/ROE6_PILOT_OUTCOME_SUMMARY.md").read_text(encoding="utf-8")

    assert "Feedback memory decision" in text
    assert "not verification" in text
