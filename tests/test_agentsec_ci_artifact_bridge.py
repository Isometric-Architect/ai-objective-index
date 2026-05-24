from pathlib import Path

from ai_objective_index.agentsec.ci_artifact_bridge import (
    AgentSecCiArtifactBridgeRequest,
    audit_agentsec3_action_manifest,
    run_ci_artifact_bridge,
    run_sample,
)
from ai_objective_index.agentsec.policy_gate import SAMPLE_MANIFEST_SET


def test_agentsec3_run_sample_blocks_policy_risk_without_external_actions():
    result = run_sample()

    assert result.decision == "BLOCK_AGENTSEC3_POLICY_RISK"
    assert result.policy_gate_decision == "BLOCK_AGENTSEC2_POLICY_RISK"
    assert result.live_mcp_called is False
    assert result.external_tool_executed is False
    assert result.github_api_used_by_agentsec is False
    assert result.token_printed is False


def test_agentsec3_missing_manifest_set_holds():
    result = run_ci_artifact_bridge(AgentSecCiArtifactBridgeRequest(manifest_set_path=""))

    assert result.decision == "HOLD_AGENTSEC3_MANIFEST_SET_REQUIRED"
    assert result.external_actions_performed is False


def test_agentsec3_clean_manifest_passes_bridge(tmp_path):
    manifest_path = tmp_path / "manifest_set.json"
    manifest_path.write_text(
        '[{"name":"local metadata helper","id":"fixture.local/local-metadata-helper","permissions":{"network_access":false,"file_access":false,"write_access":false,"secret_access":false,"browser_access":false,"code_execution":false}}]',
        encoding="utf-8",
    )

    result = run_ci_artifact_bridge(
        AgentSecCiArtifactBridgeRequest(
            manifest_set_path=str(manifest_path),
            output_dir="public_launch/agentsec3",
            profile="developer_default",
        )
    )

    assert result.decision == "PASS_AGENTSEC3_CI_ARTIFACT_BRIDGE"
    assert result.policy_gate_decision == "PASS_AGENTSEC2_POLICY_GATE"


def test_agentsec3_sample_manifest_set_fixture_is_mixed():
    assert len(SAMPLE_MANIFEST_SET) == 3


def test_agentsec3_action_manifest_audit_passes_and_no_active_workflow():
    result = audit_agentsec3_action_manifest()

    assert result["decision"] == "PASS_AGENTSEC3_ACTION_MANIFEST_SAFE"
    assert result["manifest_exists"] is True
    assert result["example_workflow_exists"] is True
    assert result["active_workflow_created"] is False
    assert not Path(".github/workflows/agentsec-policy-gate-artifact.yml").exists()
