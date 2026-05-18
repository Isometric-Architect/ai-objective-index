from ai_objective_index.extractor.action_object_builder import build_action_object_from_extracted_pages
from ai_objective_index.extractor.source_trace_mapper import make_trace


def test_action_object_builder_defaults_to_extracted_unverified() -> None:
    pages = [
        {
            "url": "https://example.com/tool",
            "title": "Fixture Tool",
            "text": "Fixture Tool has API docs and a free plan.",
            "page_type": "homepage",
        }
    ]
    fields = {
        "name": "Fixture Tool",
        "summary": "Fixture Tool is a source-traced fixture API.",
        "capabilities": ["api_access"],
        "api_available": True,
        "free_plan_found": True,
        "pricing_model": "usage_based",
        "docs_url_found": True,
    }
    traces = [
        make_trace(
            object_id="fixture_tool",
            field="pricing",
            value="free plan",
            source_url="https://example.com/tool",
            source_title="Fixture Tool",
            source_text="Fixture Tool has API docs and a free plan.",
            confidence=0.8,
        )
    ]

    action_object = build_action_object_from_extracted_pages("fixture_tool", pages, fields, traces)

    assert action_object.status == "EXTRACTED_UNVERIFIED"
    assert action_object.source_urls == ["https://example.com/tool"]
    assert action_object.missing_fields
    assert action_object.confidence == 0.8

