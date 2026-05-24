from pathlib import Path

from ai_objective_index.qira.ci_evidence_bridge import (
    QiraCiEvidenceBridgeRequest,
    audit_qira7_action_manifest,
    run_ci_evidence_bridge,
    run_sample,
)
from ai_objective_index.qira.packet_generator import generate_packet_from_request, sample_generation_request


def test_qira7_run_sample_passes_bridge():
    result = run_sample()

    assert result.decision == "PASS_QIRA7_CI_EVIDENCE_BRIDGE"
    assert result.validation_decision == "PASS_CI_EVIDENCE_ACCEPTED"
    assert result.release_gate_decision == "PASS_CONTRACT_SCOPED"
    assert result.commands_executed_by_qira is False
    assert result.github_api_used_by_qira is False


def test_qira7_missing_packet_holds():
    result = run_ci_evidence_bridge(QiraCiEvidenceBridgeRequest(packet_path=""))

    assert result.decision == "HOLD_QIRA7_PACKET_REQUIRED"
    assert result.external_actions_performed is False


def test_qira7_failed_ci_blocks(tmp_path):
    generated = generate_packet_from_request(sample_generation_request())
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(generated.packet.model_dump_json(by_alias=True), encoding="utf-8")

    result = run_ci_evidence_bridge(
        QiraCiEvidenceBridgeRequest(
            packet_path=str(packet_path),
            output_dir="public_launch/qira7",
            check_name="pytest",
            check_command="python -m pytest tests/test_example.py",
            check_status="fail",
            exit_code=1,
        )
    )

    assert result.decision == "BLOCK_QIRA7_CI_EVIDENCE"
    assert result.validation_decision == "BLOCK_CI_EVIDENCE_FAILED"


def test_qira7_manifest_audit_passes_and_no_active_workflow():
    result = audit_qira7_action_manifest()

    assert result["decision"] == "PASS_QIRA7_ACTION_MANIFEST_SAFE"
    assert result["manifest_exists"] is True
    assert result["example_workflow_exists"] is True
    assert result["active_workflow_created"] is False
    assert not Path(".github/workflows/qira-ci-evidence-bridge.yml").exists()
