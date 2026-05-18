from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from .missing_fields import list_missing_fields
from .models import ActionObject, ObjectiveScore, SourceTrace
from .scoring import score_object


def compute_source_trace_coverage(objects: list[ActionObject], traces: list[SourceTrace]) -> float:
    if not objects:
        return 0.0
    traced_object_ids = {trace.object_id for trace in traces}
    return round(
        sum(1 for action_object in objects if action_object.object_id in traced_object_ids)
        / len(objects),
        4,
    )


def compute_status_counts(objects: list[ActionObject]) -> dict[str, int]:
    return dict(Counter(str(action_object.status) for action_object in objects))


def compute_missing_field_stats(objects: list[ActionObject]) -> dict[str, Any]:
    by_field: Counter[str] = Counter()
    objects_with_missing_fields: list[dict[str, Any]] = []

    for action_object in objects:
        fields = [item.field for item in list_missing_fields(action_object)]
        by_field.update(fields)
        if fields:
            objects_with_missing_fields.append(
                {
                    "object_id": action_object.object_id,
                    "name": action_object.name,
                    "missing_fields": fields,
                    "missing_count": len(fields),
                }
            )

    objects_with_missing_fields.sort(key=lambda item: item["missing_count"], reverse=True)
    return {
        "total_missing_fields": sum(by_field.values()),
        "unique_missing_fields": len(by_field),
        "objects_with_missing_fields_count": len(objects_with_missing_fields),
        "by_field": dict(by_field.most_common()),
        "objects_with_missing_fields": objects_with_missing_fields,
    }


def _score_value(score: ObjectiveScore | dict[str, Any] | float | int) -> float:
    if isinstance(score, ObjectiveScore):
        return float(score.objective_score)
    if isinstance(score, dict):
        return float(score.get("objective_score", 0))
    return float(score)


def compute_score_distribution(
    scores: list[ObjectiveScore | dict[str, Any] | float | int],
) -> dict[str, Any]:
    values = [_score_value(score) for score in scores]
    buckets = {"0-24": 0, "25-49": 0, "50-74": 0, "75-100": 0}
    for value in values:
        if value < 25:
            buckets["0-24"] += 1
        elif value < 50:
            buckets["25-49"] += 1
        elif value < 75:
            buckets["50-74"] += 1
        else:
            buckets["75-100"] += 1

    return {
        "count": len(values),
        "min": round(min(values), 2) if values else None,
        "max": round(max(values), 2) if values else None,
        "average": round(mean(values), 2) if values else None,
        "buckets": buckets,
    }


def compute_top_objects_by_score(
    objects: list[ActionObject],
    traces: list[SourceTrace],
    query: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    traces_by_object: dict[str, list[SourceTrace]] = {}
    for trace in traces:
        traces_by_object.setdefault(trace.object_id, []).append(trace)

    rows = []
    for action_object in objects:
        score = score_object(
            action_object,
            query=query,
            traces=traces_by_object.get(action_object.object_id, []),
        )
        rows.append(
            {
                "object_id": action_object.object_id,
                "name": action_object.name,
                "object_type": action_object.object_type,
                "objective_score": score.objective_score,
                "confidence": score.confidence,
                "status": score.status,
                "rank_reason": score.rank_reason,
                "missing_fields": score.missing_fields,
            }
        )

    rows.sort(key=lambda item: item["objective_score"], reverse=True)
    return rows[:limit]


def compute_pricing_clarity_summary(objects: list[ActionObject]) -> dict[str, Any]:
    pricing_model_counts: Counter[str] = Counter()
    free_plan_found = 0
    starting_price_found = 0
    missing_pricing = []
    missing_rate_limits = []

    for action_object in objects:
        pricing = action_object.pricing or {}
        policies = action_object.policies or {}
        model = str(pricing.get("model") or "missing")
        pricing_model_counts[model] += 1
        if pricing.get("free_tier") is True:
            free_plan_found += 1
        if pricing.get("starting_price_usd") is not None:
            starting_price_found += 1
        if not pricing or not pricing.get("model"):
            missing_pricing.append(action_object.object_id)
        if not policies.get("rate_limits"):
            missing_rate_limits.append(action_object.object_id)

    return {
        "object_count": len(objects),
        "free_plan_found": free_plan_found,
        "starting_price_found": starting_price_found,
        "pricing_model_counts": dict(pricing_model_counts),
        "missing_pricing": missing_pricing,
        "missing_rate_limits": missing_rate_limits,
    }


def compute_docs_quality_summary(objects: list[ActionObject]) -> dict[str, Any]:
    docs_url_count = 0
    api_reference_count = 0
    quickstart_count = 0
    missing_docs = []

    for action_object in objects:
        docs = action_object.docs or {}
        if docs.get("docs_url"):
            docs_url_count += 1
        if docs.get("api_reference_url"):
            api_reference_count += 1
        if docs.get("quickstart_url"):
            quickstart_count += 1
        if not docs.get("docs_url"):
            missing_docs.append(action_object.object_id)

    return {
        "object_count": len(objects),
        "docs_url_count": docs_url_count,
        "api_reference_count": api_reference_count,
        "quickstart_count": quickstart_count,
        "missing_docs": missing_docs,
    }


def compute_policy_clarity_summary(objects: list[ActionObject]) -> dict[str, Any]:
    fields = ["commercial_use", "data_retention", "rate_limits", "terms_url", "privacy_url"]
    counts = {field: 0 for field in fields}
    weak_policy_objects = []

    for action_object in objects:
        policies = action_object.policies or {}
        present_count = 0
        for field in fields:
            if policies.get(field):
                counts[field] += 1
                present_count += 1
        if present_count < len(fields):
            weak_policy_objects.append(
                {
                    "object_id": action_object.object_id,
                    "name": action_object.name,
                    "present_policy_fields": present_count,
                }
            )

    return {
        "object_count": len(objects),
        "field_counts": counts,
        "fully_documented_policy_count": len(objects) - len(weak_policy_objects),
        "weak_policy_objects": weak_policy_objects,
    }

