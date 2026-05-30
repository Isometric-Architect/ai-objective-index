from ai_objective_index.portfolio.pilot_outreach_claim_guard import run_outreach_claim_audit
from ai_objective_index.portfolio.pilot_outreach_drafts import build_outreach_drafts, generate_outreach_pack


def test_outreach_drafts_generated_for_required_personas():
    drafts = build_outreach_drafts()
    assert len(drafts) == 6
    assert {draft["draft_id"] for draft in drafts} >= {"general", "agentsec", "qira", "datacapsule"}
    assert all(draft["manual_post_required"] is True for draft in drafts)
    assert all(draft["auto_send_performed"] is False for draft in drafts)
    assert all(draft["external_api_used"] is False for draft in drafts)


def test_outreach_drafts_are_conservative_and_claim_clean():
    result = generate_outreach_pack(write_result=True)
    assert result["drafts"]["draft_count"] == 6
    assert "feedback" in result["drafts"]["drafts"][0]["body"].lower()
    assert result["claim_audit"]["decision"] == "PASS_OUTREACH_CLAIM_BOUNDARY_CLEAN"
    assert run_outreach_claim_audit(write_result=False)["decision"] == "PASS_OUTREACH_CLAIM_BOUNDARY_CLEAN"
