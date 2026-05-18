from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ai_objective_index.missing_fields import list_missing_fields
from ai_objective_index.models import ActionObject, ObjectStatus, ObjectType, SourceTrace


def _merge_extracted_fields(extracted_fields: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
    if isinstance(extracted_fields, dict):
        return dict(extracted_fields)

    merged: dict[str, Any] = {
        "capabilities": [],
        "docs_links": [],
        "api_links": [],
        "github_links": [],
    }
    bool_keys = {
        "free_plan_found",
        "trial_available",
        "api_available",
        "docs_url_found",
        "pricing_url_found",
        "terms_url_found",
        "privacy_url_found",
        "commercial_use_found",
        "rate_limits_found",
        "mcp_support",
        "open_source",
        "github_url_found",
        "license_found",
        "refund_policy_found",
        "data_retention_found",
    }

    for fields in extracted_fields:
        for key, value in fields.items():
            if key in {"capabilities", "docs_links", "api_links", "github_links"}:
                existing = merged.setdefault(key, [])
                for item in value or []:
                    if item not in existing:
                        existing.append(item)
            elif key in bool_keys:
                merged[key] = bool(merged.get(key)) or bool(value)
            elif key == "starting_price_usd":
                if value is None:
                    continue
                current = merged.get(key)
                merged[key] = value if current is None else min(current, value)
            elif value not in (None, "", [], {}) and not merged.get(key):
                merged[key] = value

    return merged


def _first_page_url(pages: list[dict[str, Any]], page_type: str) -> str | None:
    for page in pages:
        if page.get("page_type") == page_type and page.get("url"):
            return page["url"]
    return None


def build_action_object_from_extracted_pages(
    object_id: str,
    pages: list[dict[str, Any]],
    extracted_fields: dict[str, Any] | list[dict[str, Any]],
    traces: list[SourceTrace],
) -> ActionObject:
    merged = _merge_extracted_fields(extracted_fields)
    source_urls = []
    for page in pages:
        url = page.get("url")
        if url and url not in source_urls:
            source_urls.append(url)

    official_url = _first_page_url(pages, "homepage") or (source_urls[0] if source_urls else None)
    docs_url = (merged.get("docs_links") or [None])[0] or _first_page_url(pages, "docs")
    api_reference_url = (merged.get("api_links") or [None])[0] or _first_page_url(pages, "api_reference")
    github_url = (merged.get("github_links") or [None])[0] or _first_page_url(pages, "github_readme")

    pricing: dict[str, Any] = {}
    if merged.get("pricing_model"):
        pricing["model"] = merged["pricing_model"]
    if "free_plan_found" in merged:
        pricing["free_tier"] = bool(merged["free_plan_found"])
    if merged.get("trial_available"):
        pricing["trial_available"] = True
    if merged.get("starting_price_usd") is not None:
        pricing["starting_price_usd"] = merged["starting_price_usd"]

    policies: dict[str, Any] = {}
    if merged.get("commercial_use_found"):
        policies["commercial_use"] = "Commercial-use language found in extracted public text."
    if merged.get("rate_limits_found"):
        policies["rate_limits"] = "Rate-limit language found in extracted public text."
    if merged.get("terms_url_found"):
        policies["terms_url"] = _first_page_url(pages, "terms") or official_url
    if merged.get("privacy_url_found"):
        policies["privacy_url"] = _first_page_url(pages, "privacy") or official_url
    if merged.get("refund_policy_found"):
        policies["refund_policy"] = "Refund or billing terms language found in extracted public text."
    if merged.get("data_retention_found"):
        policies["data_retention"] = "Data-retention language found in extracted public text."
    if merged.get("license_found"):
        policies["license"] = "License language found in extracted public text."

    docs: dict[str, Any] = {}
    if docs_url:
        docs["docs_url"] = docs_url
    if api_reference_url:
        docs["api_reference_url"] = api_reference_url
    if github_url:
        docs["github_url"] = github_url

    capabilities = list(merged.get("capabilities") or [])
    categories = ["ai_tools", "extracted_fixture"]
    if merged.get("mcp_support"):
        categories.append("mcp_servers")
        object_type: ObjectType = ObjectType.MCPServer
    elif merged.get("api_available") or "api_access" in capabilities:
        categories.append("api")
        object_type = ObjectType.APIObject
    else:
        object_type = ObjectType.ToolObject

    confidence = round(
        sum(trace.confidence for trace in traces) / len(traces),
        3,
    ) if traces else 0.45

    action_object = ActionObject(
        object_id=object_id,
        name=merged.get("name") or object_id.replace("_", " ").title(),
        object_type=object_type,
        summary=merged.get("summary") or "Extracted from local Package 6A fixtures.",
        official_url=official_url,
        source_urls=source_urls,
        capabilities=capabilities,
        categories=categories,
        pricing=pricing,
        policies=policies,
        docs=docs,
        status=ObjectStatus.EXTRACTED_UNVERIFIED,
        confidence=confidence,
        missing_fields=[],
        last_checked_at=datetime.now(UTC).isoformat(),
        source_rank="B",
    )
    missing = [item.field for item in list_missing_fields(action_object)]
    return action_object.model_copy(update={"missing_fields": missing})

