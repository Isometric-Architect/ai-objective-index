from ai_objective_index.portfolio.pilot_dashboard_builder import generate_dashboard
from ai_objective_index.portfolio.pilot_dashboard_claim_audit import run_dashboard_claim_audit, scan_dashboard_claim_text


def test_dashboard_claim_audit_passes_current_artifacts():
    generate_dashboard(write_result=True)
    result = run_dashboard_claim_audit(write_result=True)
    assert result["decision"] == "PASS_CLAIM_BOUNDARY_CLEAN"


def test_dashboard_claim_audit_blocks_overclaim_fixture():
    findings = scan_dashboard_claim_text("This is security certified.", "fixture")
    assert findings
