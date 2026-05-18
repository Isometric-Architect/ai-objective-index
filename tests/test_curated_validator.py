from __future__ import annotations

from ai_objective_index.curated_loader import load_curated_objects, load_curated_source_traces
from ai_objective_index.curated_validator import (
    BLOCK_VERIFIED_WITHOUT_VERIFICATION,
    HOLD_MISSING_TRACE,
    HOLD_PLACEHOLDER,
    PASS_CURATED_CANDIDATE,
    validate_curated_object,
)
from ai_objective_index.models import ActionObject, SourceTrace


def _candidate(status: str = "EXTRACTED_UNVERIFIED", confidence: float = 0.7) -> ActionObject:
    return ActionObject.model_validate(
        {
            "object_id": "curated-real-candidate",
            "name": "Curated Real Candidate",
            "object_type": "APIObject",
            "summary": "Manual source-traced candidate for AI API evaluation.",
            "official_url": "https://example.com/candidate",
            "source_urls": ["https://example.com/candidate"],
            "capabilities": ["api", "docs"],
            "categories": ["ai_apis"],
            "status": status,
            "confidence": confidence,
            "missing_fields": [],
        }
    )


def _trace() -> SourceTrace:
    return SourceTrace.model_validate(
        {
            "trace_id": "trace-curated-real-candidate-home",
            "object_id": "curated-real-candidate",
            "field": "summary",
            "source_url": "https://example.com/candidate",
            "source_title": "Candidate Home",
            "source_snippet": "Manual source-traced candidate for AI API evaluation.",
            "retrieved_at": "2026-05-05T00:00:00+00:00",
            "confidence": 0.8,
            "source_rank": "A",
        }
    )


def test_placeholder_object_yields_hold_placeholder() -> None:
    action_object = load_curated_objects()[0]
    traces = load_curated_source_traces()

    result = validate_curated_object(action_object, traces)

    assert result["token"] == HOLD_PLACEHOLDER
    assert result["public_beta_ready"] is False


def test_verified_without_verification_yields_block() -> None:
    result = validate_curated_object(_candidate(status="VERIFIED"), [_trace()])

    assert result["token"] == BLOCK_VERIFIED_WITHOUT_VERIFICATION
    assert result["status"] == "BLOCK"


def test_missing_trace_yields_hold_missing_trace() -> None:
    result = validate_curated_object(_candidate(), [])

    assert result["token"] == HOLD_MISSING_TRACE
    assert result["public_beta_ready"] is False


def test_valid_curated_candidate_with_trace_passes() -> None:
    result = validate_curated_object(_candidate(), [_trace()])

    assert result["token"] == PASS_CURATED_CANDIDATE
    assert result["public_beta_ready"] is True
