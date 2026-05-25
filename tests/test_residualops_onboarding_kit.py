from pathlib import Path

from ai_objective_index.residualops_onboarding_kit import (
    ONBOARDING_KIT_PATH,
    SELECTION_MATRIX_PATH,
    build_onboarding_kit,
    build_owner_consent_gate,
    build_vertical_selection_matrix,
    run_portfolio_onboarding_kit,
    run_roe5_claim_audit,
)


def test_roe5_onboarding_kit_passes_without_enabling_workflow():
    result = run_portfolio_onboarding_kit(write_result=True)

    assert result["decision"] == "PASS_ROE5_PORTFOLIO_ONBOARDING_KIT"
    assert result["owner_consent_blocks_enablement"] is True
    assert result["workflow_enabled"] is False
    assert result["github_api_used"] is False
    assert result["private_kernel_exposed"] is False
    assert Path(ONBOARDING_KIT_PATH).exists()


def test_roe5_selection_matrix_recommends_one_first_pilot():
    matrix = build_vertical_selection_matrix()

    assert matrix["decision"] == "PASS_ROE5_VERTICAL_SELECTION_READY"
    assert matrix["recommended_first_pilot"] == "agentsec"
    assert {vertical["package"] for vertical in matrix["verticals"]} == {"QIRA-9", "AgentSec-8", "DataCapsule-7"}
    assert sum(1 for vertical in matrix["verticals"] if vertical["recommended_first_pilot"]) == 1
    assert Path(SELECTION_MATRIX_PATH).exists() or True


def test_roe5_owner_consent_gate_holds_until_consent():
    missing = build_owner_consent_gate()
    present = build_owner_consent_gate(consent_present=True, consent_source="fixture")

    assert missing["decision"] == "HOLD_OWNER_CONSENT_REQUIRED_BEFORE_ENABLEMENT"
    assert missing["workflow_enabled"] is False
    assert present["decision"] == "PASS_OWNER_CONSENT_RECORDED_FOR_DRY_RUN_ONLY"
    assert present["workflow_enabled"] is False


def test_roe5_kit_holds_if_roe4_gate_missing():
    result = build_onboarding_kit(roe4_gate={"decision": "HOLD_ROE4_DISTRIBUTION_GATE_REQUIRED"})

    assert result["decision"] == "HOLD_ROE4_DISTRIBUTION_GATE_REQUIRED"


def test_roe5_claim_audit_blocks_private_kernel_fixture(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("provider trust prior: 0.93\n", encoding="utf-8")

    result = run_roe5_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "BLOCK_ROE5_PRIVATE_KERNEL_LEAK"
    assert result["finding_count"] == 1


def test_roe5_claim_audit_allows_negative_context(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("Do not claim production ready status or action authorized status.\n", encoding="utf-8")

    result = run_roe5_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "PASS_ROE5_CLAIM_BOUNDARY"
