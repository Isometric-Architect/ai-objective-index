from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .integrated_eval import run_integrated_eval, save_integrated_eval_results
from .integrated_store import get_store_for_scope
from .missing_fields import list_missing_fields
from .report_metrics import compute_missing_field_stats
from .scoring import score_object


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path(path: str | Path) -> Path:
    destination = Path(path)
    if destination.is_absolute():
        return destination
    return _repo_root() / destination


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "No rows."
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(column, "")) for column in columns) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def generate_integrated_report(
    path: str | Path = "data/generated/integrated_report_v0_2.md",
    scope: str = "integrated",
) -> Path:
    store = get_store_for_scope(scope)
    objects = store.list_objects()
    traces = []
    for action_object in objects:
        traces.extend(store.get_traces(action_object.object_id))
    eval_results = run_integrated_eval(scope=scope)
    save_integrated_eval_results(eval_results)

    status_counts = dict(Counter(str(item.status) for item in objects))
    generated_count = sum(1 for item in objects if str(item.status) == "EXTRACTED_UNVERIFIED")
    missing_stats = compute_missing_field_stats(objects)
    top_rows = []
    for action_object in objects:
        score = score_object(action_object, query="developer-friendly AI tool comparison", traces=store.get_traces(action_object.object_id))
        top_rows.append(
            {
                "object_id": action_object.object_id,
                "name": action_object.name,
                "status": score.status,
                "score": score.objective_score,
                "missing": len(list_missing_fields(action_object)),
            }
        )
    top_rows.sort(key=lambda item: item["score"], reverse=True)

    content = f"""# Integrated Generated Extraction Report v0.2

## What Package 6C Integrates

Package 6C integrates Package 6A generated fixture extraction outputs into explicit local AOI helper flows. Generated records can be searched, scored, compared, explained, and evaluated when callers choose `generated` or `integrated` scope.

## Scope

- Data scope: `{scope}`
- Object count: `{len(objects)}`
- Trace count: `{len(traces)}`
- Generated EXTRACTED_UNVERIFIED object count: `{generated_count}`

## Data Sources

- sample seed data from Package 0/1
- generated fixture extraction data from Package 6A

## Status Labels

Status counts: `{status_counts}`

Generated fixture records remain `EXTRACTED_UNVERIFIED`. They are not verified supplier claims.

## EXTRACTED_UNVERIFIED Warning

`EXTRACTED_UNVERIFIED` means a record was produced by local fixture extraction and source-trace mapping. It does not mean the supplier verified the claim, and it does not mean the data is complete, current, or safe for production decisions.

## Top Example Results

{_table(top_rows[:10], ["object_id", "name", "status", "score", "missing"])}

## Missing Fields Summary

- Total missing-field signals: `{missing_stats["total_missing_fields"]}`
- Objects with missing fields: `{missing_stats["objects_with_missing_fields_count"]}`
- Most common missing fields: `{missing_stats["by_field"]}`

## Integrated Eval Summary

- Query count: `{eval_results["query_count"]}`
- Result count: `{eval_results["result_count"]}`
- Average score: `{eval_results["average_score"]}`
- Source trace coverage: `{eval_results["source_trace_coverage"]}`
- Top result names: `{eval_results["top_result_names"]}`

## Limitations

- No live crawling.
- No network fetch.
- No external LLM extraction.
- Generated fixture records are local test artifacts.
- Source traces support fields but do not guarantee correctness or currentness.
- Objective scores are fit heuristics, not quality guarantees.

## Not Implemented

- live crawling
- supplier verification
- Hugging Face publishing
- community posting
- payment, booking, login, email sending, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification
"""
    destination = _path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content.rstrip() + "\n", encoding="utf-8")
    return destination


def main() -> None:
    path = generate_integrated_report()
    print("Integrated report generated")
    print(f"wrote: {path}")


if __name__ == "__main__":
    main()
