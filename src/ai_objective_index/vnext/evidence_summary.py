from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.models import ActionObject, SourceTrace


EvidenceStatus = Literal[
    "NO_TRACE",
    "PARTIAL_TRACE",
    "SOURCE_TRACED",
    "OFFICIAL_TRACE_AVAILABLE",
    "STALE_OR_INCOMPLETE",
]


class CapabilityEvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AOI_CapabilityEvidenceSummary/v0.1", alias="schema")
    official_source_count: int = 0
    source_trace_count: int = 0
    source_trace_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    docs_found: bool = False
    pricing_found: bool = False
    policy_found: bool = False
    repository_found: bool = False
    license_found: bool = False
    examples_found: bool = False
    last_checked_at: str | None = None
    evidence_status: EvidenceStatus = "NO_TRACE"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_notes: list[str] = Field(default_factory=list)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        lowered = value.strip().lower()
        return bool(lowered) and lowered not in {"unknown", "none", "n/a", "null"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _trace_fields(traces: list[SourceTrace]) -> set[str]:
    return {trace.field for trace in traces}


def build_evidence_summary(
    action_object: ActionObject,
    traces: list[SourceTrace],
) -> CapabilityEvidenceSummary:
    docs = action_object.docs or {}
    pricing = action_object.pricing or {}
    policies = action_object.policies or {}
    fields = _trace_fields(traces)
    official_source_count = int(bool(action_object.official_url)) + sum(
        1 for url in action_object.source_urls if "github.com" not in url.lower()
    )
    docs_found = _has_value(docs.get("docs_url")) or _has_value(docs.get("api_reference_url"))
    pricing_found = _has_value(pricing) and _has_value(pricing.get("model"))
    policy_found = any(
        _has_value(policies.get(key))
        for key in ("commercial_use", "privacy_url", "terms_url", "data_retention", "rate_limits")
    )
    repository_found = any("github" in url.lower() for url in action_object.source_urls)
    license_found = _has_value(policies.get("license")) or _has_value(policies.get("terms_url"))
    examples_found = any("example" in field or "quickstart" in field for field in fields) or _has_value(
        docs.get("quickstart_url")
    )
    important_fields = {
        "summary",
        "capabilities",
        "docs",
        "pricing",
        "policies",
        "repository",
        "install",
    }
    covered_roots = {field.split(".")[0] for field in fields}
    coverage = len(covered_roots & important_fields) / len(important_fields)

    notes: list[str] = []
    if not traces:
        status: EvidenceStatus = "NO_TRACE"
        confidence = min(0.2, float(action_object.confidence) * 0.4)
        notes.append("No source traces were available; this cannot be treated as verified.")
    elif official_source_count > 0 and coverage >= 0.25:
        status = "OFFICIAL_TRACE_AVAILABLE"
        confidence = min(0.85, max(0.45, float(action_object.confidence)) + min(0.15, len(traces) * 0.01))
    elif coverage > 0:
        status = "SOURCE_TRACED" if coverage >= 0.2 else "PARTIAL_TRACE"
        confidence = min(0.75, max(0.35, float(action_object.confidence)) + min(0.1, len(traces) * 0.01))
    else:
        status = "PARTIAL_TRACE"
        confidence = min(0.55, max(0.25, float(action_object.confidence)))

    if not docs_found:
        notes.append("Documentation evidence is missing or weak.")
    if not policy_found:
        notes.append("Policy evidence is missing or weak.")
    if not pricing_found:
        notes.append("Pricing evidence is missing or weak; this is a hold signal, not a quality judgement.")

    return CapabilityEvidenceSummary(
        official_source_count=official_source_count,
        source_trace_count=len(traces),
        source_trace_coverage=round(max(0.0, min(1.0, coverage)), 3),
        docs_found=docs_found,
        pricing_found=pricing_found,
        policy_found=policy_found,
        repository_found=repository_found,
        license_found=license_found,
        examples_found=examples_found,
        last_checked_at=str(action_object.last_checked_at) if action_object.last_checked_at else None,
        evidence_status=status,
        confidence=round(confidence, 3),
        evidence_notes=notes,
    )
