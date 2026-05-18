from __future__ import annotations

from ai_objective_index.models import ActionObject
from ai_objective_index.registry_intake.mcp_registry_client import load_raw_registry_fixture
from ai_objective_index.registry_intake.mcp_registry_evidence_gate import (
    BLOCK_FORBIDDEN_STATUS,
    BLOCK_NO_TRACE,
    HOLD_FIXTURE_ONLY,
    PASS_REGISTRY_CANDIDATE,
    evidence_gate_registry_public_beta,
    validate_registry_object,
)
from ai_objective_index.registry_intake.mcp_registry_loader import normalize_registry_records
from ai_objective_index.registry_intake.mcp_registry_mapper import (
    registry_record_to_action_object,
    registry_record_to_source_traces,
)


def _live_like_object_and_traces():
    record = dict(normalize_registry_records(load_raw_registry_fixture())[0])
    record.pop("fixture_only", None)
    action_object = registry_record_to_action_object(record)
    traces = registry_record_to_source_traces(record)
    return action_object, traces


def test_fixture_only_is_not_public_beta_ready() -> None:
    record = normalize_registry_records(load_raw_registry_fixture())[0]
    action_object = registry_record_to_action_object({**record, "fixture_only": True})
    traces = registry_record_to_source_traces({**record, "fixture_only": True})

    result = evidence_gate_registry_public_beta(action_object, traces)

    assert result["token"] == HOLD_FIXTURE_ONLY
    assert result["public_beta_ready"] is False


def test_no_trace_blocks_registry_public_beta() -> None:
    action_object, _traces = _live_like_object_and_traces()

    result = validate_registry_object(action_object, [])

    assert result["token"] == BLOCK_NO_TRACE
    assert result["status"] == "BLOCK"


def test_valid_metadata_with_trace_passes_registry_candidate_gate() -> None:
    action_object, traces = _live_like_object_and_traces()

    result = validate_registry_object(action_object, traces)

    assert result["token"] == PASS_REGISTRY_CANDIDATE
    assert result["public_beta_ready"] is True


def test_verified_or_action_ready_is_blocked() -> None:
    action_object, traces = _live_like_object_and_traces()
    payload = action_object.model_dump(mode="json")
    payload["status"] = "VERIFIED"

    result = validate_registry_object(ActionObject.model_validate(payload), traces)

    assert result["token"] == BLOCK_FORBIDDEN_STATUS
