from __future__ import annotations

from typing import Any

from .models import CompareResult
from .scoring import score_object


_DEFAULT_COMPARE_FIELDS = [
    "name",
    "object_type",
    "summary",
    "pricing",
    "policies",
    "docs",
    "status",
    "confidence",
]


def compare_objects(
    store: Any,
    object_ids: list[str],
    compare_fields: list[str] | None = None,
    query: str | None = None,
    objective: Any = None,
    constraints: dict[str, Any] | None = None,
) -> CompareResult:
    compare_fields = compare_fields or _DEFAULT_COMPARE_FIELDS
    comparison_table: list[dict[str, Any]] = []
    score_summary: list[dict[str, Any]] = []
    missing_fields_summary: dict[str, list[str]] = {}
    warnings: list[str] = []

    for object_id in object_ids:
        action_object = store.get_object(object_id)
        if action_object is None:
            warnings.append(f"Object not found: {object_id}")
            continue

        traces = store.get_traces(object_id)
        score = score_object(
            action_object,
            query=query,
            objective=objective,
            constraints=constraints,
            traces=traces,
        )

        row = {"object_id": object_id}
        for field in compare_fields:
            row[field] = getattr(action_object, field, None)
        row["objective_score"] = score.objective_score
        comparison_table.append(row)

        score_summary.append(
            {
                "object_id": object_id,
                "name": action_object.name,
                "objective_score": score.objective_score,
                "status": score.status,
                "rank_reason": score.rank_reason,
            }
        )
        missing_fields_summary[object_id] = score.missing_fields
        warnings.extend(score.warnings)

    score_summary.sort(key=lambda item: item["objective_score"], reverse=True)
    best_for = []
    if score_summary:
        top = score_summary[0]
        best_for.append(
            f"{top['name']} is currently the strongest objective-fit candidate in this comparison."
        )

    unique_warnings = list(dict.fromkeys(warnings))
    return CompareResult(
        comparison_table=comparison_table,
        best_for=best_for,
        missing_fields_summary=missing_fields_summary,
        warnings=unique_warnings,
        score_summary=score_summary,
    )

