from ai_objective_index.qira.input_packet import (
    QiraTaskPacket,
    extract_changed_files_from_diff,
    packet_to_contract_and_patch,
    sample_task_packet,
)


def test_extract_changed_files_from_unified_diff():
    diff = """diff --git a/src/app.py b/src/app.py
--- a/src/app.py
+++ b/src/app.py
diff --git a/tests/test_app.py b/tests/test_app.py
--- a/tests/test_app.py
+++ b/tests/test_app.py
"""

    assert extract_changed_files_from_diff(diff) == ["src/app.py", "tests/test_app.py"]


def test_packet_to_contract_and_patch_derives_changed_files_from_diff():
    packet = sample_task_packet()
    contract_payload, patch_payload = packet_to_contract_and_patch(packet)

    assert contract_payload["task"] == packet.task
    assert "src/ai_objective_index/qira/task_cli.py" in patch_payload["changed_files"]
    assert patch_payload["tests_passed"] is True


def test_task_packet_serializes_schema_alias():
    packet = QiraTaskPacket(task="local task")
    payload = packet.model_dump(mode="json", by_alias=True)

    assert payload["schema"] == "QIRA_TaskPacket/v0.1"
    assert packet.resolved_packet_id().startswith("qira-task-")
