from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .claim_ceiling import claim_ceiling_not_asserted_list, infer_claim_ceiling
from .missing_fields import list_missing_fields
from .models import ActionObject, ObjectStatus, ObjectiveScore, SourceTrace
from .obstruction_certificate import build_obstructions
from .source_trace import source_rank_to_weight, summarize_source_trace_coverage


_STOPWORDS = {
    "a",
    "an",
    "and",
    "api",
    "apis",
    "for",
    "find",
    "in",
    "of",
    "or",
    "the",
    "to",
    "tool",
    "tools",
    "with",
}

_UNSAFE_WORDS = {
    "guaranteed",
    "official standard",
    "automatic purchase",
    "auto purchase",
    "payment execution",
    "booking execution",
    "contract signing",
    "legal advice",
    "medical advice",
    "financial advice",
}

_DEFAULT_WEIGHTS = {
    "relevance": 0.2,
    "cost_fit": 0.12,
    "policy_clarity": 0.12,
    "documentation_quality": 0.12,
    "trust_signal": 0.1,
    "source_trace_coverage": 0.12,
    "freshness": 0.08,
    "capability_fit": 0.1,
    "structuredness": 0.04,
}


def _value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _status_text(status: ObjectStatus | str | None) -> str:
    return str(_value(status or "")).upper()


def _clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def _tokens(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, dict):
        text = " ".join(str(item) for pair in value.items() for item in pair)
    elif isinstance(value, (list, tuple, set)):
        text = " ".join(str(item) for item in value)
    else:
        text = str(value)
    text = re.sub(r"[_/-]+", " ", text.lower())
    return {token for token in re.findall(r"[a-z0-9]+", text) if token not in _STOPWORDS}


def _object_tokens(action_object: ActionObject) -> set[str]:
    parts = [
        action_object.name,
        action_object.summary,
        _value(action_object.object_type),
        " ".join(action_object.capabilities),
        " ".join(action_object.categories),
    ]
    return _tokens(" ".join(str(part) for part in parts if part))


def _query_tokens(query: str | None, objective: Any) -> set[str]:
    return _tokens(query) | _tokens(objective)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        lowered = value.strip().lower()
        return bool(lowered) and lowered not in {"unknown", "none", "n/a", "null"}
    if isinstance(value, (dict, list, tuple, set)):
        return bool(value)
    return True


def _trace_fields(traces: list[SourceTrace]) -> set[str]:
    return {trace.field for trace in traces}


def _has_trace_for(traces: list[SourceTrace], field: str) -> bool:
    return any(
        trace.field == field
        or trace.field.startswith(f"{field}.")
        or field.startswith(f"{trace.field}.")
        for trace in traces
    )


def _extract_budget(constraints: dict[str, Any] | None) -> float | None:
    if not constraints:
        return None
    for key in (
        "max_monthly_budget_usd",
        "max_budget_usd",
        "budget_usd",
        "monthly_budget_usd",
        "budget",
    ):
        value = constraints.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _relevance_score(action_object: ActionObject, query: str | None, objective: Any) -> float:
    desired = _query_tokens(query, objective)
    if not desired:
        return 50.0
    overlap = desired & _object_tokens(action_object)
    return _clamp((len(overlap) / len(desired)) * 100)


def _capability_fit(action_object: ActionObject, query: str | None, objective: Any) -> float:
    desired = _query_tokens(query, objective)
    if not desired:
        return 50.0
    capability_tokens = _tokens(action_object.capabilities)
    if not capability_tokens:
        return 20.0
    overlap = desired & capability_tokens
    return _clamp((len(overlap) / max(1, len(desired))) * 100)


def _cost_fit(action_object: ActionObject, constraints: dict[str, Any] | None) -> float:
    pricing = action_object.pricing or {}
    if not pricing or not _has_value(pricing.get("model")):
        return 25.0

    score = 55.0
    if pricing.get("free_tier") is True:
        score += 25
    if _has_value(pricing.get("starting_price_usd")):
        score += 10

    budget = _extract_budget(constraints)
    price = pricing.get("starting_price_usd")
    if budget is not None and isinstance(price, (int, float)):
        if float(price) <= budget:
            score += 15
        else:
            score -= min(35, (float(price) - budget) / max(budget, 1) * 25)

    return _clamp(score)


def _policy_clarity(action_object: ActionObject, traces: list[SourceTrace]) -> float:
    policies = action_object.policies or {}
    fields = ["commercial_use", "data_retention", "rate_limits", "terms_url", "privacy_url"]
    present = sum(1 for field in fields if _has_value(policies.get(field)))
    trace_bonus = sum(1 for field in fields if _has_trace_for(traces, f"policies.{field}"))
    return _clamp((present / len(fields)) * 80 + trace_bonus * 4)


def _documentation_quality(action_object: ActionObject, traces: list[SourceTrace]) -> float:
    docs = action_object.docs or {}
    fields = ["docs_url", "api_reference_url", "quickstart_url"]
    present = sum(1 for field in fields if _has_value(docs.get(field)))
    score = (present / len(fields)) * 80
    if any("github" in url.lower() for url in action_object.source_urls):
        score += 8
    if any(trace.field.startswith("docs") for trace in traces):
        score += 8
    if any("readme" in trace.source_title.lower() for trace in traces):
        score += 4
    return _clamp(score)


def _trust_signal(action_object: ActionObject, traces: list[SourceTrace]) -> float:
    score = 35.0
    if _has_value(action_object.official_url):
        score += 20
    if any("github" in url.lower() for url in action_object.source_urls):
        score += 12
    score += source_rank_to_weight(action_object.source_rank) * 15
    if action_object.confidence >= 0.8:
        score += 12
    elif action_object.confidence < 0.5:
        score -= 15
    if traces:
        score += min(10, len(traces) * 2)
    return _clamp(score)


def _source_trace_coverage(action_object: ActionObject, traces: list[SourceTrace]) -> float:
    coverage = summarize_source_trace_coverage(action_object, traces)
    return _clamp(float(coverage["coverage_ratio"]) * 100)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _freshness(action_object: ActionObject) -> float:
    status = _status_text(action_object.status)
    if status in {"STALE", "DEPRECATED"}:
        return 20.0
    checked_at = _parse_datetime(action_object.last_checked_at)
    if checked_at is None:
        return 35.0
    age_days = max(0, (datetime.now(UTC) - checked_at).days)
    if age_days <= 90:
        return 100.0
    if age_days <= 365:
        return 70.0
    if age_days <= 730:
        return 40.0
    return 20.0


def _structuredness(action_object: ActionObject) -> float:
    required_values = [
        action_object.object_id,
        action_object.name,
        action_object.object_type,
        action_object.summary,
        action_object.official_url,
        action_object.source_urls,
        action_object.capabilities,
        action_object.categories,
        action_object.pricing,
        action_object.policies,
        action_object.docs,
        action_object.status,
        action_object.confidence,
        action_object.last_checked_at,
    ]
    present = sum(1 for value in required_values if _has_value(value))
    return _clamp((present / len(required_values)) * 100)


def _unsafe_claim_detected(action_object: ActionObject) -> bool:
    haystack = " ".join(
        [
            action_object.name,
            action_object.summary,
            str(action_object.policies or {}),
            str(action_object.docs or {}),
        ]
    ).lower()
    return any(word in haystack for word in _UNSAFE_WORDS)


def _weights(scoring_profile: str | dict[str, Any]) -> dict[str, float]:
    if isinstance(scoring_profile, dict):
        weights = scoring_profile.get("weights", scoring_profile)
        merged = dict(_DEFAULT_WEIGHTS)
        for key, value in weights.items():
            if key in merged and isinstance(value, (int, float)):
                merged[key] = float(value)
        total = sum(merged.values())
        if total > 0:
            return {key: value / total for key, value in merged.items()}
    return dict(_DEFAULT_WEIGHTS)


def score_object(
    action_object: ActionObject,
    query: str | None = None,
    objective: Any = None,
    constraints: dict[str, Any] | None = None,
    traces: list[SourceTrace] | None = None,
    scoring_profile: str | dict[str, Any] = "default",
) -> ObjectiveScore:
    traces = traces or []
    missing = list_missing_fields(action_object)
    missing_names = [item.field for item in missing]
    status = _status_text(action_object.status)

    score_components = {
        "relevance": _relevance_score(action_object, query, objective),
        "cost_fit": _cost_fit(action_object, constraints),
        "policy_clarity": _policy_clarity(action_object, traces),
        "documentation_quality": _documentation_quality(action_object, traces),
        "trust_signal": _trust_signal(action_object, traces),
        "source_trace_coverage": _source_trace_coverage(action_object, traces),
        "freshness": _freshness(action_object),
        "capability_fit": _capability_fit(action_object, query, objective),
        "structuredness": _structuredness(action_object),
    }

    penalties = {
        "missing_field_penalty": min(25.0, len(missing_names) * 2.5),
        "stale_penalty": 15.0 if status in {"STALE", "DEPRECATED"} else 0.0,
        "unsafe_claim_penalty": 30.0
        if status == "BLOCKED"
        else (15.0 if _unsafe_claim_detected(action_object) else 0.0),
        "ambiguity_penalty": 10.0
        if action_object.confidence < 0.5 or len(action_object.summary.strip()) < 40
        else 0.0,
    }

    weights = _weights(scoring_profile)
    weighted = sum(score_components[key] * weights[key] for key in weights)
    objective_score = _clamp(weighted - sum(penalties.values()))

    rank_reason: list[str] = []
    if score_components["relevance"] >= 65:
        rank_reason.append("Strong keyword relevance to the stated objective.")
    elif score_components["relevance"] >= 35:
        rank_reason.append("Partial relevance to the stated objective.")
    else:
        rank_reason.append("Limited keyword relevance to the stated objective.")

    if score_components["cost_fit"] >= 75:
        rank_reason.append("Pricing information appears compatible with the requested constraints.")
    if score_components["documentation_quality"] >= 70:
        rank_reason.append("Documentation fields are relatively complete.")
    if score_components["source_trace_coverage"] > 0:
        rank_reason.append("At least one important field is backed by source traces.")

    warnings = [
        "Objective score is a v0.1 fit heuristic, not a quality guarantee."
    ]
    if status in {"UNVERIFIED", "EXTRACTED_UNVERIFIED"}:
        warnings.append(f"Object status is {status}; verify source traces before production use.")
    if status in {"STALE", "DEPRECATED"}:
        warnings.append("Object appears stale and received a freshness penalty.")
    if status == "BLOCKED":
        warnings.append("Object is blocked and received an unsafe-claim penalty.")
    if not traces:
        warnings.append("No source traces were provided for this scoring run.")
    if missing_names:
        warnings.append(f"Missing or weak fields detected: {', '.join(missing_names[:6])}.")
    if action_object.confidence < 0.6:
        warnings.append("Object confidence is low or ambiguous.")

    claim_ceiling = infer_claim_ceiling(action_object, traces)
    obstructions = build_obstructions(action_object, traces)

    return ObjectiveScore(
        object_id=action_object.object_id,
        objective_score=round(objective_score, 2),
        score_components={key: round(value, 2) for key, value in score_components.items()},
        penalties={key: round(value, 2) for key, value in penalties.items()},
        rank_reason=rank_reason,
        warnings=warnings,
        missing_fields=missing_names,
        confidence=action_object.confidence,
        status=_value(action_object.status),
        trace_fields=sorted(_trace_fields(traces)),
        claim_ceiling=claim_ceiling.value,
        obstructions=[item.model_dump(mode="json") for item in obstructions],
        not_asserted=claim_ceiling_not_asserted_list(claim_ceiling),
    )
