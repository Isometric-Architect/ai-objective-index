from pathlib import Path

from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack
from ai_objective_index.portfolio.roe17_external_share_gate import run_roe17_gate


def test_roe17_docs_and_outputs_exist():
    generate_external_share_pack(write_result=True)
    run_roe17_gate(write_result=True, ensure_share_pack=False)
    expected = [
        "docs/portfolio/roe17_external_safe_demo_share_pack.md",
        "docs/portfolio/external_safe_demo_workflow.md",
        "docs/portfolio/external_share_claim_boundaries.md",
        "docs/portfolio/external_share_distribution_policy.md",
        "docs/portfolio/external_share_operator_checklist.md",
        "docs/portfolio/external_share_screenshot_video_script.md",
        "external_share_pack/README_EXTERNAL_SAFE_DEMO.md",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DEMO.html",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DEMO.md",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DASHBOARD.json",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_MANIFEST.json",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_CHECKSUMS.json",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_REDACTION_REPORT.json",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_CLAIM_AUDIT.json",
        "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DISTRIBUTION_BOUNDARY.json",
        "public_launch/roe17/ROE17_EXTERNAL_SHARE_GATE_RESULT.json",
    ]
    for item in expected:
        assert Path(item).exists()
