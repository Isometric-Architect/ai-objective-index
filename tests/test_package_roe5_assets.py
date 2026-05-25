from pathlib import Path

from ai_objective_index.residualops_onboarding_kit import run_portfolio_onboarding_kit


ROOT = Path(__file__).resolve().parents[1]


def test_roe5_docs_exist():
    for relative in [
        "docs/roe5_portfolio_onboarding_kit.md",
        "docs/residualops_external_pilot_runbook.md",
        "docs/residualops_owner_consent_gate.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe5_outputs_exist_after_generation():
    run_portfolio_onboarding_kit(write_result=True)

    for relative in [
        "public_launch/roe5/ROE5_PORTFOLIO_ONBOARDING_KIT.json",
        "public_launch/roe5/ROE5_VERTICAL_SELECTION_MATRIX.json",
        "public_launch/roe5/ROE5_OWNER_CONSENT_GATE.json",
        "public_launch/roe5/ROE5_REPOSITORY_PILOT_CHECKLIST.md",
        "public_launch/roe5/ROE5_DRY_RUN_ONBOARDING_PLAN.md",
        "public_launch/roe5/ROE5_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/roe5/ROE5_ARTIFACT_MANIFEST.json",
        "public_launch/roe5/ROE5_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe5_owner_consent_note_is_public_safe():
    run_portfolio_onboarding_kit(write_result=True)
    text = (ROOT / "public_launch/roe5/ROE5_REPOSITORY_PILOT_CHECKLIST.md").read_text(encoding="utf-8")

    assert "Owner consent gate" in text
    assert "Do not paste tokens" in text
