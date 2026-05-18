from ai_objective_index.missing_fields import list_missing_fields
from ai_objective_index.models import ActionObject, ObjectStatus


def test_missing_field_detector_returns_expected_missing_fields():
    action_object = ActionObject(
        object_id="aoi-minimal",
        name="Minimal Tool",
        object_type="api",
        summary="Minimal tool with sparse metadata.",
        official_url=None,
        source_urls=[],
        capabilities=["api_access"],
        categories=["api"],
        pricing={},
        policies={},
        docs={},
        status=ObjectStatus.UNVERIFIED,
        confidence=0.4,
        missing_fields=[],
        last_checked_at=None,
    )

    fields = {item.field for item in list_missing_fields(action_object)}

    assert "pricing" in fields
    assert "commercial_use_terms" in fields
    assert "rate_limits" in fields
    assert "privacy_policy" in fields
    assert "docs_url" in fields
    assert "api_access" in fields

