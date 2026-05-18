from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from .generated_loader import load_generated_objects
from .integrated_store import build_integrated_traces, get_store_for_scope
from .mcp_tools import search_objectives
from .missing_fields import list_missing_fields
from .models import ActionObject, SourceTrace
from .report_metrics import compute_source_trace_coverage


SCOPES = (
    "sample",
    "generated",
    "integrated",
    "curated",
    "public_beta",
    "mcp_registry",
    "public_beta_mcp",
)
FIXED_QUERIES = (
    "AI API docs pricing",
    "MCP server browser automation",
    "image generation commercial use",
)
DEFAULT_OUTPUT_PATH = Path("data/generated/datascope_qa_results_v0_2.json")


def _value(value: Any) -> str:
    return str(value.value if hasattr(value, "value") else value)


def _traces_for_scope(scope: str) -> list[SourceTrace]:
    return build_integrated_traces(
        include_sample=scope in {"sample", "integrated"},
        include_generated=scope in {"generated", "integrated"},
        include_curated=scope in {"curated", "public_beta"},
        include_mcp_registry=scope in {"mcp_registry", "public_beta_mcp"},
        public_beta_only=scope == "public_beta",
        public_beta_mcp_only=scope == "public_beta_mcp",
    )


def _generated_status_ok(objects: list[ActionObject]) -> bool:
    generated_ids = {item.object_id for item in load_generated_objects()}
    relevant = [item for item in objects if item.object_id in generated_ids]
    if not relevant:
        return True
    return all(_value(item.status).upper() == "EXTRACTED_UNVERIFIED" for item in relevant)


def _scope_payload(scope: str) -> dict[str, Any]:
    errors: list[str] = []
    store = get_store_for_scope(scope)
    objects = store.list_objects()
    traces = _traces_for_scope(scope)
    status_counts = Counter(_value(item.status) for item in objects)
    object_types = Counter(_value(item.object_type) for item in objects)
    missing_fields_count = sum(len(list_missing_fields(item)) for item in objects)

    top_result_names: dict[str, list[str]] = {}
    all_scores: list[float] = []
    searchable_ids: set[str] = set()
    for query in FIXED_QUERIES:
        try:
            result = search_objectives(query=query, limit=10, data_scope=scope)
            rows = result.get("results", [])
            top_result_names[query] = [str(row.get("name")) for row in rows[:5]]
            searchable_ids.update(str(row.get("object_id")) for row in rows if row.get("object_id"))
            all_scores.extend(float(row.get("objective_score", 0)) for row in rows)
        except Exception as exc:
            errors.append(f"{query}: {exc}")
            top_result_names[query] = []

    return {
        "object_count": len(objects),
        "trace_count": len(traces),
        "searchable_object_count": len(searchable_ids),
        "average_score": round(mean(all_scores), 2) if all_scores else 0.0,
        "status_counts": dict(status_counts),
        "object_types": dict(object_types),
        "missing_fields_count": missing_fields_count,
        "source_trace_coverage": compute_source_trace_coverage(objects, traces),
        "top_result_names": top_result_names,
        "generated_unverified_status_ok": _generated_status_ok(objects),
        "errors": errors,
    }


def run_datascope_qa() -> dict[str, Any]:
    scope_results = {scope: _scope_payload(scope) for scope in SCOPES}
    sample_count = scope_results["sample"]["object_count"]
    generated_count = scope_results["generated"]["object_count"]
    integrated_count = scope_results["integrated"]["object_count"]
    curated_count = scope_results["curated"]["object_count"]
    public_beta_count = scope_results["public_beta"]["object_count"]
    mcp_registry_count = scope_results["mcp_registry"]["object_count"]
    public_beta_mcp_count = scope_results["public_beta_mcp"]["object_count"]
    warnings = [
        "Generated data remains EXTRACTED_UNVERIFIED and is not supplier-verified.",
        "Productization Mode allows implementation, but product claims require product evidence.",
        "No live crawling or network fetch is performed by data_scope QA.",
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "productization_mode": True,
        "product_claims_require_evidence": True,
        "default_data_scope": "sample",
        "scopes": scope_results,
        "summary": {
            "scope_count": len(scope_results),
            "sample_object_count": sample_count,
            "generated_object_count": generated_count,
            "integrated_object_count": integrated_count,
            "curated_object_count": curated_count,
            "public_beta_object_count": public_beta_count,
            "mcp_registry_object_count": mcp_registry_count,
            "public_beta_mcp_object_count": public_beta_mcp_count,
            "integrated_count_at_least_sample_plus_generated": integrated_count
            >= sample_count + generated_count,
            "generated_objects_remain_extracted_unverified": all(
                scope_results[scope]["generated_unverified_status_ok"]
                for scope in ("generated", "integrated")
            ),
        },
        "warnings": warnings,
    }


def save_datascope_qa_results(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_datascope_qa()
    destination = Path(path)
    if not destination.is_absolute():
        destination = Path.cwd() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_datascope_qa()
    path = save_datascope_qa_results(results)
    summary = results["summary"]
    print(f"Saved data_scope QA results: {path}")
    print(
        "data_scope QA: "
        f"sample={summary['sample_object_count']} "
        f"generated={summary['generated_object_count']} "
        f"integrated={summary['integrated_object_count']} "
        f"curated={summary['curated_object_count']} "
        f"public_beta={summary['public_beta_object_count']} "
        f"mcp_registry={summary['mcp_registry_object_count']} "
        f"public_beta_mcp={summary['public_beta_mcp_object_count']} "
        f"live_network_used={results['live_network_used']}"
    )


if __name__ == "__main__":
    main()
