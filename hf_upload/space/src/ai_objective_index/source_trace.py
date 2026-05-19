from __future__ import annotations

from typing import Any

from .models import ActionObject, SourceRank, SourceTrace


def _trace_to_public_dict(trace: SourceTrace) -> dict[str, Any]:
    return {
        "field": trace.field,
        "source_url": trace.source_url,
        "source_title": trace.source_title,
        "source_snippet": trace.source_snippet,
        "retrieved_at": trace.retrieved_at,
        "confidence": trace.confidence,
    }


def get_source_trace(store: Any, object_id: str, field: str | None = None) -> list[dict[str, Any]]:
    return [_trace_to_public_dict(trace) for trace in store.get_traces(object_id, field=field)]


def summarize_source_trace_coverage(
    action_object: ActionObject, traces: list[SourceTrace]
) -> dict[str, Any]:
    important_fields = [
        "capabilities",
        "pricing",
        "policies.commercial_use",
        "policies.data_retention",
        "policies.rate_limits",
        "docs.docs_url",
        "docs.api_reference_url",
        "official_url",
    ]
    trace_fields = {trace.field for trace in traces}
    covered = [
        field
        for field in important_fields
        if any(trace_field == field or trace_field.startswith(field) or field.startswith(trace_field) for trace_field in trace_fields)
    ]
    coverage = len(covered) / len(important_fields) if important_fields else 0
    return {
        "object_id": action_object.object_id,
        "covered_fields": covered,
        "missing_trace_fields": [field for field in important_fields if field not in covered],
        "coverage_ratio": round(coverage, 3),
        "trace_count": len(traces),
    }


def source_rank_to_weight(source_rank: SourceRank | str | None) -> float:
    value = source_rank.value if isinstance(source_rank, SourceRank) else str(source_rank or "UNKNOWN")
    return {
        "S": 1.0,
        "A": 0.9,
        "B": 0.75,
        "C": 0.5,
        "D": 0.25,
        "UNKNOWN": 0.4,
    }.get(value.upper(), 0.4)

