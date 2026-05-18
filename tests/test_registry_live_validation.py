from __future__ import annotations

from ai_objective_index.models import ActionObject
from ai_objective_index.registry_intake.mcp_registry_client import load_raw_registry_fixture
from ai_objective_index.registry_intake.mcp_registry_loader import normalize_registry_records
from ai_objective_index.registry_intake.mcp_registry_mapper import (
    registry_record_to_action_object,
    registry_record_to_source_traces,
)
from ai_objective_index.registry_intake.registry_live_validation import (
    validate_live_objects,
    validate_live_payload_shape,
)


def test_live_payload_shape_validation_works() -> None:
    raw = load_raw_registry_fixture()

    result = validate_live_payload_shape(raw, max_servers=50)

    assert result["record_count"] >= 5
    assert result["within_max_servers"] is True
    assert not result["errors"]


def test_live_validation_flags_over_max_servers() -> None:
    raw = {"servers": [{"name": str(index)} for index in range(3)]}

    result = validate_live_payload_shape(raw, max_servers=2)

    assert result["within_max_servers"] is False
    assert result["warnings"]


def test_verified_object_is_blocked_by_live_validation() -> None:
    record = normalize_registry_records(load_raw_registry_fixture())[0]
    action_object = registry_record_to_action_object(record)
    payload = action_object.model_dump(mode="json")
    payload["status"] = "VERIFIED"
    verified = ActionObject.model_validate(payload)
    traces = registry_record_to_source_traces(record)

    result = validate_live_objects([verified], traces, max_servers=50)

    assert result["no_forbidden_status"] is False
    assert result["errors"]
