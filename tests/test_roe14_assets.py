from pathlib import Path


def test_roe14_docs_and_assets_exist():
    expected = [
        "docs/portfolio/roe14_pilot_feedback_second_run_gate.md",
        "docs/portfolio/pilot_feedback_workflow.md",
        "docs/portfolio/pilot_feedback_form.md",
        "docs/portfolio/pilot_feedback_classification.md",
        "docs/portfolio/pilot_second_run_plan.md",
        "docs/portfolio/pilot_second_run_claim_boundaries.md",
        "docs/portfolio/pilot_feedback_memory_update.md",
        "schemas/portfolio/pilot_feedback_packet.schema.json",
        "schemas/portfolio/pilot_feedback_classification.schema.json",
        "schemas/portfolio/pilot_second_run_plan.schema.json",
        "schemas/portfolio/pilot_second_run_gate.schema.json",
        "schemas/portfolio/pilot_feedback_memory_update.schema.json",
    ]
    for path in expected:
        assert Path(path).exists(), path
