from __future__ import annotations

import re
from typing import Any


def _contains(text: str, *needles: str) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def _first_price(text: str) -> float | None:
    match = re.search(r"\$(\d+(?:\.\d{1,2})?)", text)
    if not match:
        return None
    return float(match.group(1))


def _extract_name(title: str | None, text: str) -> str | None:
    if title:
        return title.split("|", 1)[0].split("-", 1)[0].strip()
    for line in text.splitlines():
        cleaned = line.strip("# ").strip()
        if cleaned:
            return cleaned[:80]
    return None


def _summary(text: str) -> str:
    cleaned = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    return (sentences[0] if sentences else cleaned)[:280]


def extract_pricing_fields(text: str) -> dict[str, Any]:
    free_plan = _contains(text, "free plan", "free tier", "free developer plan")
    trial = _contains(text, "trial", "14-day", "30-day")
    return {
        "pricing_model": "usage_based" if _contains(text, "per request", "per 1k", "usage") else "subscription",
        "free_plan_found": free_plan,
        "trial_available": trial,
        "starting_price_usd": _first_price(text),
        "rate_limits_found": _contains(text, "rate limit", "requests per minute", "rpm", "per minute"),
    }


def extract_policy_fields(text: str) -> dict[str, Any]:
    return {
        "commercial_use_found": _contains(text, "commercial use", "commercial rights", "business use"),
        "rate_limits_found": _contains(text, "rate limit", "requests per minute", "rpm", "per minute"),
        "privacy_url_found": _contains(text, "privacy policy", "privacy"),
        "terms_url_found": _contains(text, "terms of service", "terms"),
        "data_retention_found": _contains(text, "data retention", "retention"),
        "refund_policy_found": _contains(text, "refund", "billing terms"),
        "license_found": _contains(text, "mit license", "apache-2.0", "license"),
    }


def extract_docs_fields(text: str, links: list[str] | None = None) -> dict[str, Any]:
    links = links or []
    docs_links = [link for link in links if _contains(link, "docs", "documentation")]
    api_links = [link for link in links if _contains(link, "api", "reference")]
    github_links = [link for link in links if "github.com" in link.lower()]
    return {
        "api_available": _contains(text, "api", "endpoint", "sdk"),
        "docs_url_found": bool(docs_links) or _contains(text, "documentation", "docs", "quickstart"),
        "api_docs_url_found": bool(api_links) or _contains(text, "api reference", "endpoint"),
        "github_url_found": bool(github_links) or _contains(text, "github", "open source"),
        "docs_links": docs_links,
        "api_links": api_links,
        "github_links": github_links,
    }


def extract_capabilities(text: str) -> list[str]:
    capability_keywords = {
        "image_generation": ["image generation", "text to image", "generate images"],
        "ocr": ["ocr", "optical character recognition", "document text"],
        "api_access": ["api", "endpoint", "sdk"],
        "commercial_use": ["commercial use", "commercial rights"],
        "mcp_support": ["mcp", "model context protocol"],
        "browser_automation": ["browser automation", "web browser"],
        "open_source": ["open source", "mit license", "apache-2.0"],
        "rate_limits": ["rate limit", "requests per minute"],
    }
    found: list[str] = []
    for capability, needles in capability_keywords.items():
        if any(_contains(text, needle) for needle in needles):
            found.append(capability)
    return found


def extract_tool_fields(source_doc: dict[str, Any]) -> dict[str, Any]:
    text = source_doc.get("text", "")
    title = source_doc.get("title")
    links = source_doc.get("links", [])
    pricing = extract_pricing_fields(text)
    policies = extract_policy_fields(text)
    docs = extract_docs_fields(text, links=links)
    capabilities = extract_capabilities(text)

    return {
        "name": _extract_name(title, text),
        "summary": _summary(text),
        "capabilities": capabilities,
        "pricing_model": pricing["pricing_model"],
        "free_plan_found": pricing["free_plan_found"],
        "trial_available": pricing["trial_available"],
        "starting_price_usd": pricing["starting_price_usd"],
        "api_available": docs["api_available"],
        "docs_url_found": docs["docs_url_found"],
        "pricing_url_found": source_doc.get("page_type") == "pricing" or "pricing" in source_doc.get("url", "").lower(),
        "terms_url_found": policies["terms_url_found"],
        "privacy_url_found": policies["privacy_url_found"],
        "commercial_use_found": policies["commercial_use_found"],
        "rate_limits_found": pricing["rate_limits_found"] or policies["rate_limits_found"],
        "mcp_support": "mcp_support" in capabilities,
        "open_source": "open_source" in capabilities,
        "github_url_found": docs["github_url_found"],
        "docs_links": docs["docs_links"],
        "api_links": docs["api_links"],
        "github_links": docs["github_links"],
        "license_found": policies["license_found"],
        "refund_policy_found": policies["refund_policy_found"],
        "data_retention_found": policies["data_retention_found"],
    }
