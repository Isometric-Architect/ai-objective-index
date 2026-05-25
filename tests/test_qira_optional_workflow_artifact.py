from pathlib import Path

from ai_objective_index.qira.optional_workflow_artifact import (
    ACTIVE_WORKFLOW_NAMES,
    EXAMPLE_WORKFLOW_PATH,
    audit_workflow_template,
    build_qira9_optional_workflow_artifact,
    run_qira9_claim_audit,
    workflow_template,
)


def test_qira9_workflow_template_is_manual_and_artifact_only():
    text = workflow_template()

    assert "workflow_dispatch" in text
    assert "actions/upload-artifact@v4" in text
    assert "qira-ci-evidence-bridge" in text
    assert "gh pr comment" not in text.lower()
    assert "git push" not in text.lower()
    assert "mcp-publisher publish" not in text.lower()


def test_qira9_build_writes_outputs_without_active_workflow():
    result = build_qira9_optional_workflow_artifact(write_result=True)

    assert result["decision"] == "PASS_QIRA9_OPTIONAL_WORKFLOW_ARTIFACT"
    assert result["workflow_auto_enabled"] is False
    assert result["active_workflow_created"] is False
    assert result["pr_comment_posted"] is False
    assert result["can_certify_security"] is False
    assert Path(EXAMPLE_WORKFLOW_PATH).exists()
    for name in ACTIVE_WORKFLOW_NAMES:
        assert not Path(".github/workflows", name).exists()


def test_qira9_audit_blocks_active_workflow_fixture(tmp_path: Path):
    example = tmp_path / EXAMPLE_WORKFLOW_PATH
    example.parent.mkdir(parents=True)
    example.write_text(workflow_template(), encoding="utf-8")
    workflow = tmp_path / ".github" / "workflows" / next(iter(ACTIVE_WORKFLOW_NAMES))
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: active\n", encoding="utf-8")

    result = audit_workflow_template(tmp_path)

    assert result["decision"] == "BLOCK_QIRA9_WORKFLOW_UNSAFE"
    assert result["active_workflow_created"] is True


def test_qira9_claim_audit_passes_public_outputs():
    build_qira9_optional_workflow_artifact(write_result=True)
    result = run_qira9_claim_audit(write_result=True)

    assert result["decision"] == "PASS_QIRA9_CLAIM_BOUNDARY"
    assert result["risky_phrase_count"] == 0
