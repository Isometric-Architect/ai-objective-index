from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlparse

from .curated_evidence_gate import evidence_gate_for_public_beta
from .models import ActionObject, SourceTrace


PASS_CURATED_CANDIDATE = "PASS_CURATED_CANDIDATE"
HOLD_MISSING_TRACE = "HOLD_MISSING_TRACE"
HOLD_PLACEHOLDER = "HOLD_PLACEHOLDER"
HOLD_MISSING_OFFICIAL_URL = "HOLD_MISSING_OFFICIAL_URL"
BLOCK_INVALID_URL = "BLOCK_INVALID_URL"
BLOCK_VERIFIED_WITHOUT_VERIFICATION = "BLOCK_VERIFIED_WITHOUT_VERIFICATION"


def _status(action_object: ActionObject) -> str:
    return str(action_object.status.value if hasattr(action_object.status, "value") else action_object.status).upper()


def _notes(action_object: ActionObject) -> str:
    return str(getattr(action_object, "notes", "") or "").lower()


def _valid_url(url: str | None) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(_has_value(item) for item in value.values())
    if isinstance(value, list):
        return bool(value)
    return True


def _has_trace_for_prefix(traces: list[SourceTrace], prefixes: tuple[str, ...]) -> bool:
    return any(
        any(str(trace.field).startswith(prefix) for prefix in prefixes)
        for trace in traces
    )


def validate_curated_object(
    action_object: ActionObject,
    traces: list[SourceTrace] | None = None,
) -> dict[str, Any]:
    traces = traces or []
    warnings: list[str] = []
    token = PASS_CURATED_CANDIDATE
    block = False

    if not action_object.object_id:
        warnings.append("object_id missing")
        token = "BLOCK_MISSING_OBJECT_ID"
        block = True
    if not action_object.name:
        warnings.append("name missing")
        token = "BLOCK_MISSING_NAME"
        block = True
    if not action_object.official_url:
        warnings.append("official_url missing")
        token = HOLD_MISSING_OFFICIAL_URL
    elif not _valid_url(action_object.official_url):
        warnings.append("official_url must be http/https")
        token = BLOCK_INVALID_URL
        block = True
    if not traces and not block:
        token = HOLD_MISSING_TRACE
        warnings.append("source trace required for public beta readiness")
    if "placeholder" in _notes(action_object) and not block:
        token = HOLD_PLACEHOLDER
        warnings.append("placeholder object is not a public beta candidate")
    if not (0 <= action_object.confidence <= 1):
        token = "BLOCK_INVALID_CONFIDENCE"
        block = True
        warnings.append("confidence must be between 0 and 1")
    if _status(action_object) in {"VERIFIED", "ACTION_READY"}:
        token = BLOCK_VERIFIED_WITHOUT_VERIFICATION
        block = True
        warnings.append("curated records cannot be VERIFIED or ACTION_READY")
    if action_object.missing_fields is None:
        warnings.append("missing_fields list should exist")
    for trace in traces:
        if not _valid_url(trace.source_url):
            token = BLOCK_INVALID_URL
            block = True
            warnings.append(f"trace {trace.trace_id} source_url must be http/https")
    field_trace_checks = [
        ("pricing", _has_value(action_object.pricing), ("pricing",)),
        ("docs", _has_value(action_object.docs), ("docs",)),
        ("policies", _has_value(action_object.policies), ("policies", "terms", "privacy", "license")),
    ]
    for label, field_present, prefixes in field_trace_checks:
        if field_present and traces and not _has_trace_for_prefix(traces, prefixes):
            warnings.append(f"{label} fields are present but lack matching source traces")
            if token == PASS_CURATED_CANDIDATE and not block:
                token = HOLD_MISSING_TRACE

    gate = evidence_gate_for_public_beta(action_object, traces)
    public_beta_ready = bool(gate["public_beta_ready"]) and token == PASS_CURATED_CANDIDATE and not block
    if public_beta_ready:
        token = PASS_CURATED_CANDIDATE

    return {
        "object_id": action_object.object_id,
        "token": token,
        "status": "BLOCK" if token.startswith("BLOCK") else ("PASS" if public_beta_ready else "HOLD"),
        "warnings": warnings,
        "trace_count": len(traces),
        "public_beta_ready": public_beta_ready,
        "evidence_gate": gate,
    }


def validate_curated_dataset(
    objects: list[ActionObject],
    traces: list[SourceTrace],
) -> dict[str, Any]:
    traces_by_object: dict[str, list[SourceTrace]] = {}
    for trace in traces:
        traces_by_object.setdefault(trace.object_id, []).append(trace)

    object_results = [
        validate_curated_object(action_object, traces_by_object.get(action_object.object_id, []))
        for action_object in objects
    ]
    counts = Counter(result["status"] for result in object_results)
    token_counts = Counter(result["token"] for result in object_results)
    warnings = [
        warning
        for result in object_results
        for warning in result.get("warnings", [])
    ]
    return {
        "object_count": len(objects),
        "trace_count": len(traces),
        "pass_count": counts.get("PASS", 0),
        "hold_count": counts.get("HOLD", 0),
        "block_count": counts.get("BLOCK", 0),
        "token_counts": dict(token_counts),
        "warnings": warnings,
        "object_results": object_results,
        "public_beta_ready_count": sum(1 for result in object_results if result["public_beta_ready"]),
    }
