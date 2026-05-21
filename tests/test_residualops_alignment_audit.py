from ai_objective_index.residualops_alignment_audit import (
    audit_residualops_alignment_text,
    run_residualops_alignment_audit,
)


def test_residualops_alignment_blocks_action_authorization_phrase():
    text = "This executable residualops engine provides an external action license."
    result = audit_residualops_alignment_text(text)
    assert "external action license" in result["block_findings"]


def test_residualops_alignment_passes_current_docs():
    result = run_residualops_alignment_audit(write_result=True)
    assert result["decision"] in {"PASS_ALIGNED", "HOLD_ALIGNMENT_DOCS_NEEDED"}
    assert result["mcp_registry_submission_performed"] is False
