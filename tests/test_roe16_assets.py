from pathlib import Path

from ai_objective_index.portfolio.pilot_dashboard_builder import generate_dashboard


def test_roe16_docs_and_outputs_exist():
    generate_dashboard(write_result=True)
    expected = [
        "docs/portfolio/roe16_pilot_dashboard_artifact_pack.md",
        "docs/portfolio/pilot_dashboard_workflow.md",
        "docs/portfolio/pilot_dashboard_static_html.md",
        "docs/portfolio/pilot_dashboard_claim_boundaries.md",
        "docs/portfolio/pilot_dashboard_operator_checklist.md",
        "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.json",
        "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.md",
        "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.html",
        "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD_MANIFEST.json",
        "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD_CHECKSUMS.json",
        "pilot_dashboard/RESIDUALOPS_PILOT_STATUS_CARDS.json",
        "pilot_dashboard/RESIDUALOPS_PILOT_TIMELINE.json",
        "pilot_dashboard/RESIDUALOPS_PILOT_CLAIM_BOUNDARY.md",
        "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD_REDACTION_REPORT.json",
        "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD_KNOWN_LIMITS.md",
        "public_launch/roe16/ROE16_DASHBOARD_GATE_RESULT.json",
    ]
    for item in expected:
        assert Path(item).exists()
