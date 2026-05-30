from ai_objective_index.portfolio.pilot_outreach_claim_guard import (
    run_outreach_claim_audit,
    run_outreach_redaction,
    scan_outreach_claim_text,
    scan_outreach_redaction_text,
)
from ai_objective_index.portfolio.pilot_outreach_drafts import generate_outreach_pack


def test_claim_guard_blocks_overclaim_fixture():
    findings = scan_outreach_claim_text("This is production ready and security certified.", "fixture.md")
    assert findings


def test_claim_guard_allows_negated_boundary():
    findings = scan_outreach_claim_text("This is not security certification and no external action is authorized.", "fixture.md")
    assert findings == []


def test_redaction_blocks_token_like_string():
    findings = scan_outreach_redaction_text("token = sk-abcdefghijklmnopqrstuvwxyz", "fixture.md")
    assert findings


def test_outreach_audits_pass_generated_pack():
    generate_outreach_pack(write_result=True)
    assert run_outreach_claim_audit(write_result=False)["decision"] == "PASS_OUTREACH_CLAIM_BOUNDARY_CLEAN"
    assert run_outreach_redaction(write_result=False)["decision"] == "PASS_REDACTED"
