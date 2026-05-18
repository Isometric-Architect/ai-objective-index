from __future__ import annotations

from ai_objective_index.registry_intake.mcp_registry_client import load_raw_registry_fixture
from ai_objective_index.registry_intake.mcp_registry_loader import normalize_registry_records
from ai_objective_index.registry_intake.mcp_registry_mapper import (
    registry_record_to_action_object,
    registry_record_to_source_traces,
)


def test_registry_mapper_creates_mcpserver_action_object() -> None:
    record = normalize_registry_records(load_raw_registry_fixture())[0]

    action_object = registry_record_to_action_object(record)

    assert action_object.object_type == "MCPServer"
    assert action_object.status == "EXTRACTED_UNVERIFIED"
    assert "mcp_server" in action_object.categories
    assert action_object.confidence > 0


def test_registry_mapper_creates_source_traces() -> None:
    record = normalize_registry_records(load_raw_registry_fixture())[0]

    traces = registry_record_to_source_traces(record)

    assert traces
    assert {trace.field for trace in traces}.issuperset({"name", "description", "repository", "package", "capabilities"})
