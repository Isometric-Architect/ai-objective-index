import json

import pytest

from ai_objective_index.qira.input_packet import sample_task_packet
from ai_objective_index.qira.packet_loader import QiraPacketError, build_report_from_packet_file, load_task_packet


def test_load_task_packet_and_build_report(tmp_path):
    packet = sample_task_packet()
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(packet.model_dump(mode="json", by_alias=True)), encoding="utf-8")

    loaded = load_task_packet(path)
    report = build_report_from_packet_file(path)

    assert loaded.task == packet.task
    assert report.decision_token == "PASS_CONTRACT_SCOPED"
    assert report.action_license.deploy == "BLOCK"


def test_load_task_packet_rejects_non_json(tmp_path):
    path = tmp_path / "packet.txt"
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(QiraPacketError):
        load_task_packet(path)


def test_load_task_packet_rejects_invalid_payload(tmp_path):
    path = tmp_path / "packet.json"
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(QiraPacketError):
        load_task_packet(path)
