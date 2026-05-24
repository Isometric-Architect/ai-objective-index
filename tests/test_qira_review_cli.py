import json
from pathlib import Path

from ai_objective_index.qira.input_packet import sample_task_packet
from ai_objective_index.qira.review_cli import run_qira3_review, run_sample, write_sample_packet


def test_qira3_write_sample_packet():
    path = write_sample_packet()
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["schema"] == "QIRA_TaskPacket/v0.1"
    assert payload["test_commands"]


def test_qira3_sample_review_writes_outputs():
    result = run_sample()

    assert result["decision"] == "PASS_QIRA3_REVIEW"
    assert result["test_command_summary"]["commands_executed"] is False
    assert Path("public_launch/qira3/QIRA3_PATH_CLASSIFICATION_REPORT.json").exists()
    assert Path("public_launch/qira3/QIRA3_TEST_COMMAND_CONTRACT.json").exists()
    assert Path("public_launch/qira3/QIRA3_RELEASE_GATE_REPORT.json").exists()
    assert Path("public_launch/qira3/QIRA3_REVIEW_RESULT.json").exists()


def test_qira3_review_blocks_for_secret_path(tmp_path):
    packet = sample_task_packet()
    packet.changed_files = [".env"]
    packet.patch_diff = ""
    source = tmp_path / "packet.json"
    source.write_text(json.dumps(packet.model_dump(mode="json", by_alias=True)), encoding="utf-8")

    result = run_qira3_review(source, tmp_path / "report.json")

    assert result["decision"] == "BLOCK_QIRA3_REVIEW"
    assert result["path_classification_decision"] == "BLOCK_PATH_CLASSIFICATION"


def test_qira3_review_holds_for_install_command(tmp_path):
    packet = sample_task_packet()
    packet.test_commands = ["python -m pip install -r requirements.txt"]
    source = tmp_path / "packet.json"
    source.write_text(json.dumps(packet.model_dump(mode="json", by_alias=True)), encoding="utf-8")

    result = run_qira3_review(source, tmp_path / "report.json")

    assert result["decision"] == "HOLD_QIRA3_REVIEW"
    assert result["test_command_contract_decision"] == "HOLD_TEST_COMMAND_REVIEW"
