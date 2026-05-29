from pathlib import Path

from ai_objective_index.real_pypi_upload_gate import _repo_root


def test_roe12_docs_and_assets_exist():
    expected = [
        "docs/portfolio/roe12_owner_consented_pilot_intake_kit.md",
        "docs/portfolio/pilot_intake_workflow.md",
        "docs/portfolio/owner_consent_policy.md",
        "docs/portfolio/vertical_routing_policy.md",
        "docs/portfolio/pilot_intake_claim_boundaries.md",
        "docs/portfolio/pilot_intake_feedback_memory.md",
        "docs/portfolio/pilot_run_checklist.md",
        "pilot_intake/PILOT_INTAKE_PACKET_SAMPLE_AGENTSEC.json",
        "pilot_intake/PILOT_INTAKE_PACKET_SAMPLE_QIRA.json",
        "pilot_intake/PILOT_INTAKE_PACKET_SAMPLE_DATACAPSULE.json",
        "pilot_intake/PILOT_CONSENT_RECORD_TEMPLATE.md",
        "pilot_intake/PILOT_INTAKE_FORM_TEMPLATE.md",
        "pilot_intake/PILOT_RUN_PLAN_SAMPLE.json",
        "pilot_intake/PILOT_INTAKE_REDACTION_REPORT.json",
        "pilot_intake/PILOT_INTAKE_REVIEWER_INSTRUCTIONS.md",
        "pilot_intake/PILOT_INTAKE_KNOWN_LIMITS.md",
        "public_launch/roe12/ROE12_PILOT_INTAKE_GATE_RESULT.json",
        "public_launch/roe12/ROE12_PILOT_INTAKE_SUMMARY.md",
        "public_launch/roe12/ROE12_NEXT_ACTIONS.md",
    ]
    missing = [path for path in expected if not (_repo_root() / Path(path)).exists()]
    assert missing == []
