from __future__ import annotations

from ai_objective_index.registry_intake.mcp_registry_loader import (
    detect_registry_payload_shape,
    normalize_registry_records,
)


def test_registry_loader_supports_common_shapes() -> None:
    rows = [{"name": "a"}, {"name": "b"}]

    assert normalize_registry_records({"servers": rows}) == rows
    assert normalize_registry_records({"items": rows}) == rows
    assert normalize_registry_records({"data": rows}) == rows
    assert normalize_registry_records(rows) == rows
    assert normalize_registry_records({"payload": {"servers": rows}}) == rows


def test_registry_loader_respects_max_servers() -> None:
    rows = [{"name": str(index)} for index in range(5)]

    result = normalize_registry_records({"servers": rows}, max_servers=2)

    assert len(result) == 2


def test_detect_registry_payload_shape() -> None:
    shape = detect_registry_payload_shape({"servers": [{"name": "a"}]})

    assert shape["shape"] == "object.servers"
    assert shape["record_count"] == 1
