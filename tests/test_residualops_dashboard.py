from ai_objective_index.residualops_artifact_manifest import run_shared_artifact_manifest
from ai_objective_index.residualops_dashboard import run_vertical_status_dashboard
from ai_objective_index.residualops_dashboard_audit import run_dashboard_audit


def test_vertical_status_dashboard_builds_from_manifest():
    run_shared_artifact_manifest(write_result=True)
    result = run_vertical_status_dashboard(write_result=True)

    assert result["decision"] == "PASS_ROE2_DASHBOARD_READY"
    assert result["vertical_count"] == 3
    assert result["status_counts"]["block_risk"] >= 1
    assert result["external_actions_performed"] is False


def test_dashboard_audit_passes_current_outputs():
    run_shared_artifact_manifest(write_result=True)
    run_vertical_status_dashboard(write_result=True)
    result = run_dashboard_audit(write_result=True)

    assert result["decision"] == "PASS_ROE2_DASHBOARD_AUDIT"
    assert result["issues"] == []
    assert result["risky_phrase_count"] == 0
