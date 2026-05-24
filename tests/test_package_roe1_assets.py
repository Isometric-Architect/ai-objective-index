from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_roe1_docs_exist():
    for relative in [
        "docs/roe1_surface_alignment_gate.md",
        "docs/residualops_common_kernel.md",
        "docs/residualops_vertical_surface_matrix.md",
    ]:
        assert (ROOT / relative).exists()


def test_roe1_outputs_exist_after_generation():
    for relative in [
        "public_launch/roe1/ROE1_VERTICAL_SURFACE_INVENTORY.json",
        "public_launch/roe1/ROE1_SURFACE_ALIGNMENT_GATE.json",
        "public_launch/roe1/ROE1_PUBLIC_PRIVATE_ALIGNMENT_AUDIT.json",
        "public_launch/roe1/ROE1_SUMMARY.md",
        "public_launch/roe1/ROE1_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists()


def test_roe1_summary_preserves_no_external_action_boundary():
    summary = (ROOT / "public_launch/roe1/ROE1_SUMMARY.md").read_text(encoding="utf-8")

    assert "does not upload packages" in summary
    assert "does not enable workflows" in summary
