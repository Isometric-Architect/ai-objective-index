from ai_objective_index.portfolio.datacapsule_pilot_packager import build_datacapsule_pilot_receipt
from ai_objective_index.portfolio.datacapsule_pilot_receipt import to_jsonable


def test_datacapsule_pilot_receipt_serializes():
    payload = to_jsonable(build_datacapsule_pilot_receipt(sample=True))

    assert payload["schema"] == "ResidualOps_DataCapsulePilotReceipt/v0.1"
    assert payload["decision_summary"]["allow_count"] == 1
    assert payload["decision_summary"]["hold_count"] == 1
    assert payload["decision_summary"]["block_count"] == 1
    assert payload["raw_content_inspected"] is False
    assert payload["can_authorize_training"] is False
    assert payload["can_authorize_action"] is False
