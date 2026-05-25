from pathlib import Path

from ai_objective_index.datacapsule.optional_workflow_artifact import (
    ACTIVE_WORKFLOW_NAMES,
    EXAMPLE_WORKFLOW_PATH,
    audit_workflow_template,
    build_datacapsule7_optional_workflow_artifact,
    run_datacapsule7_claim_audit,
    workflow_template,
)


def test_datacapsule7_workflow_template_is_manual_and_artifact_only():
    text = workflow_template()

    assert "workflow_dispatch" in text
    assert "actions/upload-artifact@v4" in text
    assert "datacapsule-corpus-manifest-artifact" in text
    assert "gh pr comment" not in text.lower()
    assert "git push" not in text.lower()
    assert "mcp-publisher publish" not in text.lower()


def test_datacapsule7_build_writes_outputs_without_active_workflow():
    result = build_datacapsule7_optional_workflow_artifact(write_result=True)

    assert result["decision"] == "PASS_DATACAPSULE7_OPTIONAL_WORKFLOW_ARTIFACT"
    assert result["workflow_auto_enabled"] is False
    assert result["active_workflow_created"] is False
    assert result["review_comment_posted"] is False
    assert result["can_certify_privacy"] is False
    assert Path(EXAMPLE_WORKFLOW_PATH).exists()
    for name in ACTIVE_WORKFLOW_NAMES:
        assert not Path(".github/workflows", name).exists()


def test_datacapsule7_audit_blocks_active_workflow_fixture(tmp_path: Path):
    example = tmp_path / EXAMPLE_WORKFLOW_PATH
    example.parent.mkdir(parents=True)
    example.write_text(workflow_template(), encoding="utf-8")
    workflow = tmp_path / ".github" / "workflows" / next(iter(ACTIVE_WORKFLOW_NAMES))
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: active\n", encoding="utf-8")

    result = audit_workflow_template(tmp_path)

    assert result["decision"] == "BLOCK_DATACAPSULE7_WORKFLOW_UNSAFE"
    assert result["active_workflow_created"] is True


def test_datacapsule7_claim_audit_passes_public_outputs():
    build_datacapsule7_optional_workflow_artifact(write_result=True)
    result = run_datacapsule7_claim_audit(write_result=True)

    assert result["decision"] == "PASS_DATACAPSULE7_CLAIM_BOUNDARY"
    assert result["risky_phrase_count"] == 0
