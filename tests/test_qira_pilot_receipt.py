from ai_objective_index.portfolio.qira_pilot_packager import build_qira_pilot_receipt, build_sample_task_packet
from ai_objective_index.portfolio.qira_pilot_receipt import to_jsonable


def test_qira_task_packet_and_receipt_serialize():
    packet = build_sample_task_packet()
    receipt = build_qira_pilot_receipt(sample=True)
    payload = to_jsonable(receipt)

    assert packet.model_dump(mode="json", by_alias=True)["schema"] == "ResidualOps_QIRA_TaskPacket/v0.1"
    assert payload["schema"] == "ResidualOps_QIRA_PilotReceipt/v0.1"
    assert payload["decision_summary"]["allow_count"] == 1
    assert payload["decision_summary"]["hold_count"] == 1
    assert payload["decision_summary"]["block_count"] == 1
    assert payload["can_authorize_merge"] is False
    assert payload["can_authorize_deploy"] is False
