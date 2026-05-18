import pytest
from pydantic import ValidationError

from ai_objective_index.models import ActionObject, SourceTrace
from ai_objective_index.seed_loader import load_sample_index


def test_action_object_loads_from_sample_object():
    sample = load_sample_index()[0]

    assert isinstance(sample, ActionObject)
    assert sample.object_id == "aoi-pixelforge-api"
    assert sample.pricing["free_tier"] is True


def test_source_trace_confidence_validation_works():
    with pytest.raises(ValidationError):
        SourceTrace(
            trace_id="trace-invalid",
            object_id="aoi-invalid",
            field="pricing",
            source_url="https://example.com",
            source_title="Example",
            source_snippet="Invalid confidence.",
            retrieved_at="2026-04-28T00:00:00Z",
            confidence=1.5,
        )

