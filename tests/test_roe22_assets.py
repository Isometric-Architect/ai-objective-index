from pathlib import Path

from ai_objective_index.portfolio.external_share_refresh_archive import run_refresh_archive
from ai_objective_index.portfolio.external_share_refresh_builder import generate_external_share_refresh
from ai_objective_index.portfolio.roe22_external_share_refresh_gate import run_roe22_gate


def test_roe22_assets_exist():
    generate_external_share_refresh(write_result=True)
    run_refresh_archive(dry_run=True, build=False, write_result=True)
    result = run_roe22_gate(write_result=True, ensure_share_refresh=False)
    assert result["decision"] == "PASS_EXTERNAL_SHARE_PACK_REFRESHED_FROM_UPDATED_DASHBOARD"
    required = [
        "docs/portfolio/roe22_external_share_pack_refresh_from_updated_dashboard.md",
        "docs/portfolio/external_share_refresh_workflow.md",
        "docs/portfolio/external_share_refresh_delta.md",
        "docs/portfolio/external_share_v2_claim_boundaries.md",
        "docs/portfolio/external_share_v2_distribution_policy.md",
        "docs/portfolio/external_share_v2_operator_checklist.md",
        "docs/portfolio/external_share_v2_screenshot_video_script.md",
        "schemas/portfolio/external_share_refresh.schema.json",
        "schemas/portfolio/external_share_refresh_delta.schema.json",
        "schemas/portfolio/external_share_refresh_manifest.schema.json",
        "schemas/portfolio/external_share_refresh_gate.schema.json",
        "external_share_pack_v2/README_EXTERNAL_SAFE_DEMO_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DASHBOARD_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_STATUS_CARDS_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_TIMELINE_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_FEEDBACK_MEMORY_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_CLAIM_BOUNDARY_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_KNOWN_LIMITS_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_OPERATOR_SCRIPT_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_SCREENSHOT_SCRIPT_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_VIDEO_SCRIPT_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_MANIFEST_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_CHECKSUMS_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_REDACTION_REPORT_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_CLAIM_AUDIT_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DISTRIBUTION_BOUNDARY_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_REFRESH_DELTA_V2.json",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_SHARE_DECISION_V2.md",
        "external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_ARCHIVE_RESULT_V2.json",
        "public_launch/roe22/ROE22_EXTERNAL_SHARE_REFRESH_GATE_RESULT.json",
        "public_launch/roe22/ROE22_EXTERNAL_SHARE_REFRESH_SUMMARY.md",
        "public_launch/roe22/ROE22_NEXT_ACTIONS.md",
    ]
    for path in required:
        assert Path(path).exists(), path
