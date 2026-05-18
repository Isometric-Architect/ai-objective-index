from __future__ import annotations

from pathlib import Path

from ai_objective_index.curated_loader import (
    load_curated_objects,
    load_curated_source_traces,
    normalize_curated_object,
)


def test_curated_loader_loads_placeholder_rows() -> None:
    objects = load_curated_objects()
    traces = load_curated_source_traces()

    assert objects
    assert traces
    assert objects[0].status == "EXTRACTED_UNVERIFIED"
    assert objects[0].confidence <= 0.5


def test_curated_loader_parses_list_fields() -> None:
    action_object = normalize_curated_object(
        {
            "object_id": "curated-list-test",
            "name": "Curated List Test",
            "object_type": "APIObject",
            "summary": "Manual candidate",
            "official_url": "https://example.com/list-test",
            "capabilities": "OCR, document extraction; API",
            "categories": "ai_apis, document_ai",
            "missing_fields": "pricing, rate_limits",
            "status": "EXTRACTED_UNVERIFIED",
            "confidence": "0.6",
        }
    )

    assert "OCR" in action_object.capabilities
    assert "document extraction" in action_object.capabilities
    assert "rate_limits" in action_object.missing_fields


def test_curated_loader_tolerates_empty_files() -> None:
    empty = Path("data/curated/__test_empty.jsonl")
    try:
        empty.write_text("", encoding="utf-8")
        assert load_curated_objects(empty) == []
        assert load_curated_source_traces(empty) == []
    finally:
        empty.unlink(missing_ok=True)
