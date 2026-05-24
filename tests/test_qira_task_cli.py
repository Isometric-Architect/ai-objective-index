import json
from pathlib import Path

from ai_objective_index.qira.input_packet import sample_task_packet
from ai_objective_index.qira.task_cli import run_sample, run_task_packet_cli, write_sample_packet


def test_write_sample_packet_creates_public_sample():
    path = write_sample_packet()

    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "QIRA_TaskPacket/v0.1"


def test_run_task_packet_cli_writes_report(tmp_path):
    packet = sample_task_packet()
    source = tmp_path / "packet.json"
    output = tmp_path / "report.json"
    source.write_text(json.dumps(packet.model_dump(mode="json", by_alias=True)), encoding="utf-8")

    result = run_task_packet_cli(source, output)

    assert result["decision"] == "PASS_QIRA_PACKET_INTAKE"
    assert result["decision_token"] == "PASS_CONTRACT_SCOPED"
    assert output.exists()
    assert result["tests_executed_by_qira"] is False
    assert result["deploy_performed"] is False


def test_run_task_packet_cli_invalid_packet_blocks(tmp_path):
    source = tmp_path / "packet.json"
    source.write_text("{}", encoding="utf-8")

    result = run_task_packet_cli(source, tmp_path / "report.json")

    assert result["decision"] == "BLOCK_QIRA_PACKET_INVALID"
    assert result["external_actions_performed"] is False


def test_run_sample_writes_qira2_outputs():
    result = run_sample()

    assert result["decision"] == "PASS_QIRA_PACKET_INTAKE"
    assert Path("public_launch/qira2/QIRA2_SAMPLE_TASK_PACKET.json").exists()
    assert Path("public_launch/qira2/QIRA2_RELEASE_GATE_REPORT.json").exists()
    assert Path("public_launch/qira2/QIRA2_PACKET_INTAKE_RESULT.json").exists()
