from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ai_objective_index.models import ActionObject, SourceTrace
from ai_objective_index.scoring import score_object

from .action_object_builder import build_action_object_from_extracted_pages
from .confidence import confidence_from_source, source_rank_for_page_type
from .html_text import extract_links, extract_title, strip_html
from .page_classifier import classify_page
from .rule_extractor import extract_tool_fields
from .source_trace_mapper import map_field_to_trace


FIXTURE_OBJECTS = {
    "image_api_fixture": [
        ("image_api_home.html", "https://example.com/pixelforge"),
        ("image_api_pricing.html", "https://example.com/pixelforge/pricing"),
        ("image_api_docs.html", "https://example.com/pixelforge/docs"),
    ],
    "mcp_server_fixture": [
        ("mcp_server_readme.md", "https://github.com/example/browser-mcp-server/blob/main/README.md"),
    ],
    "ocr_api_fixture": [
        ("ocr_api_home.html", "https://example.com/clearread-ocr"),
        ("ocr_api_pricing.html", "https://example.com/clearread-ocr/pricing"),
    ],
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _fixture_dir() -> Path:
    return _repo_root() / "data" / "fixtures" / "pages"


def _generated_dir() -> Path:
    path = _repo_root() / "data" / "generated"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _markdown_links(text: str) -> list[str]:
    return re.findall(r"\]\((https?://[^)]+)\)", text)


def _source_doc(filename: str, url: str) -> dict[str, Any]:
    raw = (_fixture_dir() / filename).read_text(encoding="utf-8")
    if filename.endswith(".html"):
        title = extract_title(raw)
        text = strip_html(raw)
        links = extract_links(raw, base_url=url)
    else:
        title = next((line.strip("# ").strip() for line in raw.splitlines() if line.strip()), filename)
        text = raw
        links = _markdown_links(raw)

    page_type = classify_page(url, title=title, text=text)
    return {
        "filename": filename,
        "url": url,
        "title": title,
        "text": text,
        "links": links,
        "page_type": page_type,
    }


def _traceable_fields(fields: dict[str, Any]) -> dict[str, tuple[str, Any, str]]:
    mapping: dict[str, tuple[str, Any, str]] = {}
    if fields.get("capabilities"):
        mapping["capabilities"] = ("capabilities", ", ".join(fields["capabilities"]), "api")
    if fields.get("free_plan_found") or fields.get("starting_price_usd") is not None:
        mapping["pricing"] = ("pricing", fields.get("starting_price_usd") or "free plan", "free")
    if fields.get("commercial_use_found"):
        mapping["policies.commercial_use"] = ("policies.commercial_use", "commercial use", "commercial")
    if fields.get("rate_limits_found"):
        mapping["policies.rate_limits"] = ("policies.rate_limits", "rate limit", "rate")
    if fields.get("docs_url_found"):
        mapping["docs.docs_url"] = ("docs.docs_url", "docs", "docs")
    if fields.get("api_available"):
        mapping["docs.api_reference_url"] = ("docs.api_reference_url", "api", "api")
    if fields.get("github_url_found"):
        mapping["docs.github_url"] = ("docs.github_url", "github", "github")
    return mapping


def _extract_object(object_id: str, file_records: list[tuple[str, str]]) -> tuple[ActionObject, list[SourceTrace]]:
    pages = [_source_doc(filename, url) for filename, url in file_records]
    extracted_by_page = [extract_tool_fields(page) for page in pages]
    traces: list[SourceTrace] = []

    for page, fields in zip(pages, extracted_by_page, strict=True):
        source_rank = source_rank_for_page_type(page["page_type"])
        for field, value, keyword in _traceable_fields(fields).values():
            confidence = confidence_from_source(
                page_type=page["page_type"],
                source_rank=source_rank,
                keyword_strength=1.0 if keyword.lower() in page["text"].lower() else 0.5,
                field_presence=True,
            )
            traces.append(
                map_field_to_trace(
                    object_id=object_id,
                    field=field,
                    value=value,
                    source_doc=page,
                    confidence=confidence,
                    source_rank=source_rank,
                )
            )

    action_object = build_action_object_from_extracted_pages(
        object_id=object_id,
        pages=pages,
        extracted_fields=extracted_by_page,
        traces=traces,
    )
    return action_object, traces


def run_fixture_pipeline() -> dict[str, Any]:
    objects: list[ActionObject] = []
    traces: list[SourceTrace] = []

    for object_id, records in FIXTURE_OBJECTS.items():
        action_object, object_traces = _extract_object(object_id, records)
        objects.append(action_object)
        traces.extend(object_traces)

    scores = [
        score_object(
            action_object,
            query="developer-friendly AI tool comparison",
            objective="source-traced extracted object",
            traces=[trace for trace in traces if trace.object_id == action_object.object_id],
        )
        for action_object in objects
    ]

    generated = _generated_dir()
    object_path = generated / "extracted_objects_v0_2.json"
    trace_path = generated / "extracted_source_traces_v0_2.json"
    report_path = generated / "extraction_report_v0_2.json"

    object_payload = {"objects": [item.model_dump(mode="json") for item in objects]}
    trace_payload = {"traces": [item.model_dump(mode="json") for item in traces]}
    report_payload = {
        "version": "0.2-fixture-skeleton",
        "read_only": True,
        "network_fetch": False,
        "object_count": len(objects),
        "source_trace_count": len(traces),
        "status_counts": {"EXTRACTED_UNVERIFIED": len(objects)},
        "objective_scores": [score.model_dump(mode="json") for score in scores],
        "known_limits": [
            "Fixture pipeline only; no broad live crawling.",
            "Extracted fields are EXTRACTED_UNVERIFIED.",
            "Source traces support fields but do not guarantee correctness.",
        ],
    }

    object_path.write_text(json.dumps(object_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    trace_path.write_text(json.dumps(trace_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "objects": object_payload["objects"],
        "traces": trace_payload["traces"],
        "report": report_payload,
        "generated_files": [str(object_path), str(trace_path), str(report_path)],
    }


def main() -> None:
    result = run_fixture_pipeline()
    print("AI Objective Index fixture extraction complete")
    print(
        json.dumps(
            {
                "object_count": len(result["objects"]),
                "source_trace_count": len(result["traces"]),
                "generated_files": result["generated_files"],
                "network_fetch": False,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
