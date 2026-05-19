from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from .eval_runner import run_all_golden_queries, save_eval_results
from .missing_fields import list_missing_fields
from .report_metrics import (
    compute_docs_quality_summary,
    compute_missing_field_stats,
    compute_policy_clarity_summary,
    compute_pricing_clarity_summary,
    compute_score_distribution,
    compute_source_trace_coverage,
    compute_status_counts,
    compute_top_objects_by_score,
)
from .scoring import score_object
from .seed_loader import load_golden_queries, load_sample_index, load_source_traces


DISCLAIMER = (
    "This is a v0.1 benchmark report based on sample/extracted records. "
    "It is not a quality guarantee, official ranking, legal advice, purchasing advice, or safety certification."
)

DEFAULT_OBJECTIVE = "developer-friendly AI tool comparison"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path(path: str | Path) -> Path:
    destination = Path(path)
    if destination.is_absolute():
        return destination
    return _repo_root() / destination


def _write_text(path: str | Path, content: str) -> Path:
    destination = _path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content.rstrip() + "\n", encoding="utf-8")
    return destination


def _write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    destination = _path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _today() -> str:
    return date.today().isoformat()


def _score_all_objects() -> list[dict[str, Any]]:
    objects = load_sample_index()
    traces = load_source_traces()
    traces_by_object: dict[str, list[Any]] = {}
    for trace in traces:
        traces_by_object.setdefault(trace.object_id, []).append(trace)

    rows = []
    for action_object in objects:
        score = score_object(
            action_object,
            query=DEFAULT_OBJECTIVE,
            traces=traces_by_object.get(action_object.object_id, []),
        )
        rows.append(
            {
                "object_id": action_object.object_id,
                "name": action_object.name,
                "object_type": action_object.object_type,
                "objective": DEFAULT_OBJECTIVE,
                **score.model_dump(mode="json"),
            }
        )
    rows.sort(key=lambda item: item["objective_score"], reverse=True)
    return rows


def generate_download_json_files() -> list[Path]:
    generated_at = datetime.now(UTC).isoformat()
    objects = load_sample_index()
    traces = load_source_traces()
    queries = load_golden_queries()
    scores = _score_all_objects()

    return [
        _write_json(
            "data/downloads/action_objects_v0_1.json",
            {
                "version": "0.1.0-package-4",
                "generated_at": generated_at,
                "records": [item.model_dump(mode="json") for item in objects],
            },
        ),
        _write_json(
            "data/downloads/source_traces_v0_1.json",
            {
                "version": "0.1.0-package-4",
                "generated_at": generated_at,
                "records": [item.model_dump(mode="json") for item in traces],
            },
        ),
        _write_json(
            "data/downloads/objective_scores_v0_1.json",
            {
                "version": "0.1.0-package-4",
                "generated_at": generated_at,
                "objective": DEFAULT_OBJECTIVE,
                "records": scores,
            },
        ),
        _write_json(
            "data/downloads/golden_queries_v0_1.json",
            {
                "version": "0.1.0-package-4",
                "generated_at": generated_at,
                "records": queries,
            },
        ),
    ]


def _download_links() -> str:
    return "\n".join(
        [
            "- `data/downloads/action_objects_v0_1.json`",
            "- `data/downloads/source_traces_v0_1.json`",
            "- `data/downloads/objective_scores_v0_1.json`",
            "- `data/downloads/golden_queries_v0_1.json`",
        ]
    )


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join([header, divider, *body])


def generate_mcp_server_objective_index_report(
    path: str | Path = "reports/mcp_server_objective_index_v0_1.md",
) -> Path:
    objects = load_sample_index()
    traces = load_source_traces()
    top_objects = compute_top_objects_by_score(objects, traces, query=DEFAULT_OBJECTIVE, limit=10)
    mcp_objects = [
        {
            "object_id": item.object_id,
            "name": item.name,
            "object_type": item.object_type,
            "capabilities": ", ".join(item.capabilities[:4]),
        }
        for item in objects
        if "mcp" in str(item.object_type).lower()
        or any("mcp" in category.lower() for category in item.categories)
    ]
    coverage = compute_source_trace_coverage(objects, traces)
    missing_stats = compute_missing_field_stats(objects)
    status_counts = compute_status_counts(objects)
    score_distribution = compute_score_distribution(top_objects)

    content = f"""# MCP Server Objective Index v0.1

Date: {_today()}

{DISCLAIMER}

## What This Report Is

This report summarizes the read-only AOI benchmark sample for objective-fit comparison, with emphasis on MCP/server-like objects where present.

## Dataset Scope

- Action objects: {len(objects)}
- Source traces: {len(traces)}
- Status counts: {status_counts}

## Methodology

Records are loaded from Package 0 sample data, scored with the Package 1 objective-fit heuristic, and summarized without crawling or network calls.

## Scoring Formula Summary

The v0.1 score combines relevance, cost fit, policy clarity, documentation quality, trust signal, source trace coverage, freshness, capability fit, and structuredness, then subtracts missing-field, stale, unsafe-claim, and ambiguity penalties.

## Top Ranked Sample Objects

{_markdown_table(top_objects, ["object_id", "name", "object_type", "objective_score", "confidence"])}

## MCP/Server-Related Objects

{_markdown_table(mcp_objects, ["object_id", "name", "object_type", "capabilities"]) if mcp_objects else "No MCP/server-related objects found."}

## Source Trace Coverage

- Object-level trace coverage: {coverage}
- Score distribution among displayed top objects: {score_distribution}

## Missing Fields Summary

- Objects with missing fields: {missing_stats["objects_with_missing_fields_count"]}
- Total missing-field signals: {missing_stats["total_missing_fields"]}
- Most common missing fields: {missing_stats["by_field"]}

## Known Limitations

- Sample records are fake but realistic.
- Source traces are mock traces and do not prove completeness or currentness.
- The report is read-only and does not execute external actions.

## Download Files

{_download_links()}

## Claim Boundary

{DISCLAIMER}
"""
    return _write_text(path, content)


def generate_ai_tool_pricing_index_report(
    path: str | Path = "reports/ai_tool_pricing_index_v0_1.md",
) -> Path:
    objects = load_sample_index()
    pricing_summary = compute_pricing_clarity_summary(objects)
    policy_summary = compute_policy_clarity_summary(objects)
    free_plan_rows = [
        {
            "object_id": item.object_id,
            "name": item.name,
            "model": (item.pricing or {}).get("model"),
            "starting_price_usd": (item.pricing or {}).get("starting_price_usd"),
        }
        for item in objects
        if (item.pricing or {}).get("free_tier") is True
    ]
    missing_rows = [
        {
            "object_id": item.object_id,
            "name": item.name,
            "missing_fields": ", ".join(field.field for field in list_missing_fields(item) if field.field in {"pricing", "free_plan", "rate_limits"}),
        }
        for item in objects
    ]
    missing_rows = [row for row in missing_rows if row["missing_fields"]]

    content = f"""# AI Tool Pricing Index v0.1

Date: {_today()}

{DISCLAIMER}

## Dataset Scope

- Action objects: {len(objects)}
- Pricing models: {pricing_summary["pricing_model_counts"]}

## Pricing-Related Fields

This report checks pricing model, free-tier signal, starting price, and rate-limit policy presence.

## Tools With free_plan_found

{_markdown_table(free_plan_rows, ["object_id", "name", "model", "starting_price_usd"])}

## Pricing Clarity Summary

- Free plan found: {pricing_summary["free_plan_found"]}
- Starting price found: {pricing_summary["starting_price_found"]}
- Missing pricing records: {pricing_summary["missing_pricing"]}
- Policy field counts: {policy_summary["field_counts"]}

## Missing Pricing/Rate Limit Fields

{_markdown_table(missing_rows, ["object_id", "name", "missing_fields"]) if missing_rows else "No pricing or rate-limit missing-field signals in current sample."}

## Known Limitations

- Pricing fields are sample/extracted benchmark records.
- AOI does not provide purchasing advice or execute purchases.
- Prices and plan details are not verified live.

## Download Files

{_download_links()}
"""
    return _write_text(path, content)


def generate_source_trace_quality_report(
    path: str | Path = "reports/source_trace_quality_report_v0_1.md",
) -> Path:
    objects = load_sample_index()
    traces = load_source_traces()
    coverage = compute_source_trace_coverage(objects, traces)
    traces_by_object: dict[str, int] = Counter(trace.object_id for trace in traces)
    source_rank_distribution = Counter(str(getattr(trace, "source_rank", "UNKNOWN")) for trace in traces)
    coverage_rows = [
        {
            "object_id": item.object_id,
            "name": item.name,
            "trace_count": traces_by_object.get(item.object_id, 0),
        }
        for item in objects
    ]
    coverage_rows.sort(key=lambda item: item["trace_count"], reverse=True)
    strongest = coverage_rows[:5]
    weakest = sorted(coverage_rows, key=lambda item: item["trace_count"])[:5]

    content = f"""# Source Trace Quality Report v0.1

Date: {_today()}

{DISCLAIMER}

## What Is SourceTrace

`SourceTrace` connects an AOI object field to a source URL, title, snippet, retrieval timestamp, and confidence value.

## SourceTrace Coverage Summary

- Object-level trace coverage: {coverage}
- Trace count: {len(traces)}
- Objects: {len(objects)}

## SourceRank Distribution

{dict(source_rank_distribution)}

## Objects With Strongest Trace Coverage

{_markdown_table(strongest, ["object_id", "name", "trace_count"])}

## Objects With Weak Trace Coverage

{_markdown_table(weakest, ["object_id", "name", "trace_count"])}

## Missing Source Trace Risks

- One trace per object is enough for structural coverage but not enough for strong evidence coverage.
- Trace snippets are mock examples in Package 0 sample data.
- A trace supports a field; it does not guarantee legal, procurement, safety, or quality sufficiency.

## Known Limitations

- No crawler is implemented.
- No live source verification is performed.
- Source trace confidence is heuristic and sample-bound.

## Download Files

{_download_links()}
"""
    return _write_text(path, content)


def generate_eval_markdown_files(results: dict[str, Any] | None = None) -> list[Path]:
    if results is None:
        eval_path = _path("data/eval_results.json")
        if eval_path.exists():
            results = json.loads(eval_path.read_text(encoding="utf-8"))
        else:
            results = run_all_golden_queries()
            save_eval_results(results)

    query_rows = [
        {
            "query_id": item.get("query_id"),
            "domain": item.get("domain"),
            "query": item.get("query"),
            "structural_pass": item.get("structural_pass"),
            "relevance_pass": item.get("relevance_pass"),
        }
        for item in results.get("results", [])
    ]
    failed = [item for item in query_rows if not item["structural_pass"]]

    golden = f"""# Golden Queries

AOI golden queries are read-only benchmark prompts used to exercise objective-fit search and scoring.

## How To Run

```powershell
python -m ai_objective_index.eval_runner
```

## Queries

{_markdown_table(query_rows, ["query_id", "domain", "query", "structural_pass", "relevance_pass"])}
"""

    scoring = f"""# Scoring Eval

{DISCLAIMER}

## Summary

- Query count: {results.get("query_count")}
- Structural pass count: {results.get("structural_pass_count")}
- Structural pass rate: {results.get("structural_pass_rate")}
- Average objective score: {results.get("average_objective_score")}
- Average confidence: {results.get("average_confidence")}
- Average source trace coverage: {results.get("average_source_trace_coverage")}
"""

    if failed:
        failure_body = _markdown_table(failed, ["query_id", "domain", "query", "structural_pass", "relevance_pass"])
    else:
        failure_body = (
            "No structural failures in current sample eval.\n\n"
            "Known limitations: relevance checks are heuristic, source traces are mock traces, and sample records are not live market data."
        )
    failure_cases = f"""# Failure Cases

{DISCLAIMER}

## Structural Failures

{failure_body}
"""

    return [
        _write_text("evals/golden_queries.md", golden),
        _write_text("evals/scoring_eval.md", scoring),
        _write_text("evals/failure_cases.md", failure_cases),
    ]


def generate_all_reports() -> list[Path]:
    eval_results = run_all_golden_queries()
    save_eval_results(eval_results)
    generated = [
        generate_mcp_server_objective_index_report(),
        generate_ai_tool_pricing_index_report(),
        generate_source_trace_quality_report(),
    ]
    generated.extend(generate_download_json_files())
    generated.extend(generate_eval_markdown_files(eval_results))
    return generated


def main() -> None:
    generated = generate_all_reports()
    print("Generated Package 4 reports and downloads:")
    for path in generated:
        print(path.relative_to(_repo_root()))


if __name__ == "__main__":
    main()

