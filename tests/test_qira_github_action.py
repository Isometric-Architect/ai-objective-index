import json
from pathlib import Path

from ai_objective_index.qira.github_action import (
    audit_action_manifest,
    run_github_action_dry_run,
    write_sample_action_packet,
)
from ai_objective_index.qira.input_packet import sample_task_packet


def test_write_sample_action_packet_creates_packet():
    path = write_sample_action_packet()
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["schema"] == "QIRA_TaskPacket/v0.1"
    assert path.name == "QIRA4_SAMPLE_ACTION_PACKET.json"


def test_github_action_dry_run_sample_writes_outputs():
    result = run_github_action_dry_run(write_sample=True)

    assert result["decision"] == "PASS_QIRA_ACTION_DRY_RUN"
    assert result["github_action_wrapper"] is True
    assert result["workflow_auto_enabled"] is False
    assert result["project_commands_executed"] is False
    assert result["deploy_performed"] is False
    assert Path("public_launch/qira4/QIRA4_GITHUB_ACTION_DRY_RUN_RESULT.json").exists()
    assert Path("public_launch/qira4/QIRA4_GITHUB_ACTION_SUMMARY.md").exists()


def test_github_action_dry_run_blocks_secret_path(tmp_path):
    packet = sample_task_packet()
    packet.changed_files = [".env"]
    packet.patch_diff = ""
    source = tmp_path / "packet.json"
    source.write_text(json.dumps(packet.model_dump(mode="json", by_alias=True)), encoding="utf-8")

    result = run_github_action_dry_run(source, tmp_path)

    assert result["decision"] == "BLOCK_QIRA_ACTION_REVIEW"
    assert result["patch_applied"] is False


def test_action_manifest_audit_passes():
    result = audit_action_manifest()

    assert result["decision"] == "PASS_QIRA_ACTION_MANIFEST_SAFE"
    assert result["manifest_exists"] is True
    assert result["workflow_auto_enabled"] is False
