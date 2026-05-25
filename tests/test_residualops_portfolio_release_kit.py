from pathlib import Path

from ai_objective_index.residualops_portfolio_release_kit import (
    ARTIFACT_MANIFEST_PATH,
    OPERATOR_HANDOFF_PATH,
    PORTFOLIO_KIT_PATH,
    PUBLIC_VERTICAL_INDEX_PATH,
    RELEASE_NOTES_PATH,
    build_artifact_manifest,
    build_portfolio_release_kit,
    operator_handoff_markdown,
    release_notes_markdown,
    run_portfolio_release_kit,
)


def test_roe3_portfolio_release_kit_builds_current_verticals():
    result = build_portfolio_release_kit()

    assert result["decision"] == "PASS_ROE3_PORTFOLIO_RELEASE_KIT"
    assert result["vertical_count"] == 3
    assert {item["package"] for item in result["verticals"]} >= {"QIRA-8", "AgentSec-7", "DataCapsule-6"}
    assert result["external_actions_performed"] is False
    assert result["private_kernel_exposed"] is False
    assert result["can_authorize_action"] is False


def test_roe3_release_notes_preserve_boundary():
    kit = build_portfolio_release_kit()
    text = release_notes_markdown(kit)
    handoff = operator_handoff_markdown(kit)

    assert "ROE-3 Portfolio Release Notes" in text
    assert "does not enable workflows" in text
    assert "expose private kernels" in text
    assert "ROE-3 Operator Handoff" in handoff
    assert "anti-gaming rules" in handoff


def test_roe3_run_writes_outputs():
    result = run_portfolio_release_kit(write_result=True)

    assert result["decision"] == "PASS_ROE3_PORTFOLIO_RELEASE_KIT"
    for path in [
        PORTFOLIO_KIT_PATH,
        RELEASE_NOTES_PATH,
        PUBLIC_VERTICAL_INDEX_PATH,
        OPERATOR_HANDOFF_PATH,
        ARTIFACT_MANIFEST_PATH,
    ]:
        assert Path(path).exists(), path


def test_roe3_artifact_manifest_holds_missing_artifact():
    manifest = build_artifact_manifest([Path("public_launch/roe3/NO_SUCH_FILE.md")])

    assert manifest["decision"] == "HOLD_ROE3_ARTIFACT_MISSING"
    assert manifest["missing_artifacts"]
