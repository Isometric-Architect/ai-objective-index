from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack
from ai_objective_index.portfolio.external_share_pack_claim_audit import run_share_claim_audit, scan_share_claim_text


def test_external_share_pack_claim_audit_passes():
    generate_external_share_pack(write_result=True)
    result = run_share_claim_audit(write_result=True)
    assert result["decision"] == "PASS_CLAIM_BOUNDARY_CLEAN"


def test_external_share_pack_claim_audit_blocks_overclaim():
    findings = scan_share_claim_text("This is production ready.", "fixture")
    assert findings
