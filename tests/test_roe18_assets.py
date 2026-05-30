from pathlib import Path

from ai_objective_index.portfolio.pilot_outreach_drafts import generate_outreach_pack
from ai_objective_index.portfolio.roe18_outreach_gate import run_roe18_gate


def test_roe18_docs_and_outputs_exist():
    generate_outreach_pack(write_result=True)
    run_roe18_gate(write_result=True, ensure_pack=False)
    required = [
        "docs/portfolio/roe18_pilot_discovery_feedback_intake_outreach_drafts.md",
        "docs/portfolio/pilot_outreach_workflow.md",
        "docs/portfolio/pilot_feedback_intake_form.md",
        "docs/portfolio/pilot_feedback_triage.md",
        "docs/portfolio/pilot_outreach_claim_boundaries.md",
        "docs/portfolio/pilot_outreach_operator_checklist.md",
        "docs/portfolio/no_contact_feedback_launch_policy.md",
        "pilot_outreach/PILOT_DISCOVERY_PERSONAS.json",
        "pilot_outreach/PILOT_FEEDBACK_REQUEST_DRAFT_GENERAL.md",
        "pilot_outreach/PILOT_FEEDBACK_REQUEST_DRAFT_AGENTSEC.md",
        "pilot_outreach/PILOT_FEEDBACK_REQUEST_DRAFT_QIRA.md",
        "pilot_outreach/PILOT_FEEDBACK_REQUEST_DRAFT_DATACAPSULE.md",
        "pilot_outreach/PILOT_FEEDBACK_REQUEST_DRAFT_TECHNICAL_REVIEWER.md",
        "pilot_outreach/PILOT_FEEDBACK_REQUEST_DRAFT_FOUNDER_OR_OPERATOR.md",
        "pilot_outreach/PILOT_FEEDBACK_INTAKE_FORM_TEMPLATE.md",
        "pilot_outreach/PILOT_FEEDBACK_TRIAGE_TAXONOMY.json",
        "pilot_outreach/PILOT_LINK_PACK.md",
        "pilot_outreach/PILOT_OUTREACH_FAQ.md",
        "pilot_outreach/PILOT_OUTREACH_CLAIM_BOUNDARY.md",
        "pilot_outreach/PILOT_OUTREACH_OPERATOR_CHECKLIST.md",
        "pilot_outreach/PILOT_OUTREACH_DO_NOT_SEND_GUARD.md",
        "pilot_outreach/PILOT_OUTREACH_REDACTION_REPORT.json",
        "pilot_outreach/PILOT_OUTREACH_CLAIM_AUDIT.json",
        "pilot_outreach/PILOT_OUTREACH_KNOWN_LIMITS.md",
        "public_launch/roe18/ROE18_OUTREACH_GATE_RESULT.json",
        "public_launch/roe18/ROE18_OUTREACH_SUMMARY.md",
        "public_launch/roe18/ROE18_NEXT_ACTIONS.md",
    ]
    for item in required:
        assert Path(item).exists(), item
