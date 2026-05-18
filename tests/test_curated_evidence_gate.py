from __future__ import annotations

from ai_objective_index.curated_evidence_gate import evidence_gate_for_public_beta
from ai_objective_index.models import ActionObject, SourceTrace


def _object(official_url: str = "https://example.com/tool") -> ActionObject:
    return ActionObject.model_validate(
        {
            "object_id": "curated-gate-tool",
            "name": "Curated Gate Tool",
            "object_type": "SaaSObject",
            "summary": "Manual candidate with source traces.",
            "official_url": official_url,
            "source_urls": [official_url],
            "capabilities": ["api"],
            "categories": ["ai_tools"],
            "status": "EXTRACTED_UNVERIFIED",
            "confidence": 0.7,
            "missing_fields": [],
        }
    )


def _trace() -> SourceTrace:
    return SourceTrace.model_validate(
        {
            "trace_id": "trace-curated-gate-tool-home",
            "object_id": "curated-gate-tool",
            "field": "summary",
            "source_url": "https://example.com/tool",
            "source_title": "Tool Home",
            "source_snippet": "Manual candidate with source traces.",
            "retrieved_at": "2026-05-05T00:00:00+00:00",
            "confidence": 0.8,
        }
    )


def test_no_trace_blocks_public_beta() -> None:
    result = evidence_gate_for_public_beta(_object(), [])

    assert result["token"] == "BLOCK_MISSING_SOURCE_TRACE"
    assert result["public_beta_ready"] is False


def test_invalid_url_blocks_public_beta() -> None:
    result = evidence_gate_for_public_beta(_object("not-a-url"), [_trace()])

    assert result["token"] == "BLOCK_INVALID_URL"
    assert result["public_beta_ready"] is False


def test_good_candidate_passes_public_beta_gate() -> None:
    result = evidence_gate_for_public_beta(_object(), [_trace()])

    assert result["token"] == "PASS_PUBLIC_BETA"
    assert result["public_beta_ready"] is True
