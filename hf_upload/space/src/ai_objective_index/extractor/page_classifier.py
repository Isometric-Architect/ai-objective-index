from __future__ import annotations


def classify_page(url: str, title: str | None = None, text: str | None = None) -> str:
    haystack = " ".join([url, title or "", text or ""]).lower()

    if "github.com" in haystack and ("readme" in haystack or "/blob/" in haystack):
        return "github_readme"
    if "raw.githubusercontent.com" in haystack or haystack.strip().startswith("# "):
        return "github_readme"
    if "api reference" in haystack or "/api" in haystack or "endpoint" in haystack:
        return "api_reference"
    if "pricing" in haystack or "free plan" in haystack or "$" in haystack:
        return "pricing"
    if "privacy" in haystack:
        return "privacy"
    if "terms" in haystack or "commercial use" in haystack:
        return "terms"
    if "docs" in haystack or "documentation" in haystack or "quickstart" in haystack:
        return "docs"
    if "faq" in haystack or "frequently asked" in haystack:
        return "faq"
    if url.rstrip("/").count("/") <= 2:
        return "homepage"
    return "unknown"

