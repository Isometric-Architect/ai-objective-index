from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_roe2_docs_exist():
    for relative in [
        "docs/roe2_shared_artifact_manifest.md",
        "docs/residualops_dashboard_skeleton.md",
        "docs/residualops_artifact_bridge_policy.md",
    ]:
        assert (ROOT / relative).exists()


def test_roe2_outputs_exist_after_generation():
    for relative in [
        "public_launch/roe2/ROE2_SHARED_ARTIFACT_MANIFEST.json",
        "public_launch/roe2/ROE2_VERTICAL_STATUS_DASHBOARD.json",
        "public_launch/roe2/ROE2_VERTICAL_STATUS_DASHBOARD.md",
        "public_launch/roe2/ROE2_DASHBOARD_AUDIT.json",
        "public_launch/roe2/ROE2_SUMMARY.md",
        "public_launch/roe2/ROE2_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists()


def test_roe2_dashboard_boundary_text():
    dashboard = (ROOT / "public_launch/roe2/ROE2_VERTICAL_STATUS_DASHBOARD.md").read_text(encoding="utf-8")

    assert "does not run probes" in dashboard
    assert "authorize actions" in dashboard
