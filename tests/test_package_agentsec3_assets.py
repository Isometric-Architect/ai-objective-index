from pathlib import Path


def test_agentsec3_docs_and_actions_exist():
    for path in [
        "docs/agentsec3_ci_artifact_bridge.md",
        "docs/agentsec_github_ci_bridge_limitations.md",
        ".github/actions/agentsec-policy-gate-artifact/action.yml",
        "examples/agentsec_policy_gate_artifact_workflow.yml",
    ]:
        assert Path(path).exists(), path


def test_agentsec3_outputs_exist_after_sample():
    from ai_objective_index.agentsec.ci_artifact_bridge import audit_agentsec3_action_manifest, run_sample
    from ai_objective_index.agentsec_claim_audit import run_agentsec_claim_audit

    run_sample()
    audit_agentsec3_action_manifest()
    run_agentsec_claim_audit()

    for path in [
        "public_launch/agentsec3/AGENTSEC3_SAMPLE_MANIFEST_SET.json",
        "public_launch/agentsec3/AGENTSEC3_POLICY_GATE_RESULT.json",
        "public_launch/agentsec3/AGENTSEC3_POLICY_GATE_REPORT.md",
        "public_launch/agentsec3/AGENTSEC3_BRIDGE_RESULT.json",
        "public_launch/agentsec3/AGENTSEC3_ACTION_MANIFEST_AUDIT.json",
        "public_launch/agentsec3/AGENTSEC3_NEXT_STEPS.md",
        "public_launch/agentsec3/AGENTSEC_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path


def test_agentsec3_does_not_auto_enable_workflow():
    assert not Path(".github/workflows/agentsec-policy-gate-artifact.yml").exists()


def test_agentsec3_docs_preserve_no_api_or_token_boundary():
    text = Path("docs/agentsec3_ci_artifact_bridge.md").read_text(encoding="utf-8")

    assert "does not call live MCP servers" in text
    assert "does not call GitHub APIs" in text
    assert "handle tokens" in text
