from __future__ import annotations

from typing import Any

from .models import ActionObject, MissingField


_FIELD_GUIDANCE: dict[str, tuple[str, str, str]] = {
    "pricing": (
        "Pricing affects budget fit and makes cost comparisons auditable.",
        "Official pricing page",
        "high",
    ),
    "free_plan": (
        "Free-plan availability affects low-budget adoption and eval usage.",
        "Official pricing page or plan table",
        "medium",
    ),
    "commercial_use_terms": (
        "Commercial-use terms are needed before using outputs in business contexts.",
        "Terms of service, license page, or usage-rights page",
        "high",
    ),
    "rate_limits": (
        "Rate limits affect feasibility for agent and API workloads.",
        "API docs, pricing page, or limits page",
        "medium",
    ),
    "privacy_policy": (
        "Privacy policy coverage affects data-handling review.",
        "Official privacy policy",
        "high",
    ),
    "docs_url": (
        "Documentation quality affects integration risk and implementation effort.",
        "Official documentation",
        "medium",
    ),
    "api_access": (
        "API access determines whether an agent can integrate programmatically.",
        "API reference or developer documentation",
        "medium",
    ),
    "refund_policy": (
        "Refund terms can matter for purchasing review, even though AOI does not advise purchases.",
        "Refund policy or billing terms",
        "low",
    ),
    "data_retention_policy": (
        "Data retention terms affect privacy and operational risk review.",
        "Security, privacy, or data-retention page",
        "high",
    ),
    "github_url": (
        "A repository URL helps evaluate open-source activity and license evidence.",
        "Official repository URL",
        "medium",
    ),
    "license": (
        "License terms affect whether and how a tool can be used or redistributed.",
        "License file or license page",
        "high",
    ),
}


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        stripped = value.strip().lower()
        return bool(stripped) and stripped not in {"unknown", "n/a", "none", "null"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _guidance(field: str) -> MissingField:
    why, source, severity = _FIELD_GUIDANCE.get(
        field,
        (
            "This field may affect objective-fit scoring or downstream review.",
            "Official product documentation or policy page",
            "medium",
        ),
    )
    return MissingField(
        field=field,
        why_it_matters=why,
        recommended_source=source,
        severity=severity,  # type: ignore[arg-type]
    )


def list_missing_fields(action_object: ActionObject) -> list[MissingField]:
    pricing = action_object.pricing or {}
    policies = action_object.policies or {}
    docs = action_object.docs or {}
    source_urls = action_object.source_urls or []
    object_type = str(action_object.object_type).lower()
    capabilities = {capability.lower() for capability in action_object.capabilities}

    missing: list[str] = []

    if not _is_present(pricing) or not _is_present(pricing.get("model")):
        missing.append("pricing")
    if "free_tier" not in pricing:
        missing.append("free_plan")
    if not _is_present(policies.get("commercial_use")):
        missing.append("commercial_use_terms")
    if not _is_present(policies.get("rate_limits")):
        missing.append("rate_limits")
    if not _is_present(policies.get("privacy_url")):
        missing.append("privacy_policy")
    if not _is_present(docs.get("docs_url")):
        missing.append("docs_url")
    if ("api" in object_type or "api_access" in capabilities) and not _is_present(
        docs.get("api_reference_url")
    ):
        missing.append("api_access")
    if "refund_policy" not in policies:
        missing.append("refund_policy")
    if not _is_present(policies.get("data_retention")):
        missing.append("data_retention_policy")
    if (
        "open_source" in object_type
        or "open_source" in capabilities
        or any("open_source" in category.lower() for category in action_object.categories)
    ) and not any("github" in url.lower() for url in source_urls):
        missing.append("github_url")
    if (
        "open_source" in object_type
        or any("open_source" in category.lower() for category in action_object.categories)
    ) and not _is_present(policies.get("license")) and not _is_present(policies.get("terms_url")):
        missing.append("license")

    missing.extend(action_object.missing_fields)

    seen: set[str] = set()
    result: list[MissingField] = []
    for field in missing:
        if field in seen:
            continue
        seen.add(field)
        result.append(_guidance(field))
    return result

