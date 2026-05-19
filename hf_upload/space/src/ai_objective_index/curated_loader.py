from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ActionObject, ObjectStatus, ObjectType, SourceTrace


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _read_jsonl(path: str | Path, strict: bool = False) -> tuple[list[dict[str, Any]], list[str]]:
    resolved = _resolve(path)
    if not resolved.exists():
        return [], [f"File not found: {resolved}"]
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, line in enumerate(resolved.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                records.append(item)
            else:
                errors.append(f"line {line_number}: expected object")
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: {exc}")
    if strict and errors:
        raise ValueError("; ".join(errors))
    return records, errors


def _split_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).replace(";", ",").split(",") if item.strip()]


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _float(value: Any, default: float = 0.3) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
    return max(0.0, min(1.0, parsed))


def normalize_curated_object(row: dict[str, Any]) -> ActionObject:
    payload = dict(row)
    object_id = str(payload.get("object_id") or "").strip()
    if not object_id:
        raise ValueError("Curated object is missing object_id.")

    pricing = {
        "model": payload.get("pricing_model") or payload.get("pricing", {}).get("model") if isinstance(payload.get("pricing"), dict) else payload.get("pricing_model"),
        "free_tier": _bool(payload.get("free_plan_found")),
    }
    policies = {
        "commercial_use": "found" if _bool(payload.get("commercial_use_found")) else "",
        "rate_limits": "found" if _bool(payload.get("rate_limits_found")) else "",
        "terms_url": payload.get("terms_url") or "",
        "privacy_url": payload.get("privacy_url") or "",
        "license": payload.get("license") or "",
    }
    docs = {
        "docs_url": payload.get("docs_url") or "",
        "api_reference_url": payload.get("docs_url") if _bool(payload.get("api_available")) else "",
    }
    source_urls = [
        url
        for url in [
            payload.get("official_url"),
            payload.get("docs_url"),
            payload.get("pricing_url"),
            payload.get("terms_url"),
            payload.get("privacy_url"),
            payload.get("github_url"),
        ]
        if url
    ]
    status = str(payload.get("status") or ObjectStatus.EXTRACTED_UNVERIFIED.value).upper()
    if status in {"VERIFIED", "ACTION_READY"}:
        status = ObjectStatus.EXTRACTED_UNVERIFIED.value

    action_object = {
        "object_id": object_id,
        "name": payload.get("name") or object_id,
        "object_type": payload.get("object_type") or ObjectType.ToolObject.value,
        "summary": payload.get("summary") or "Manually curated AOI candidate.",
        "official_url": payload.get("official_url") or None,
        "source_urls": source_urls,
        "capabilities": _split_list(payload.get("capabilities")),
        "categories": _split_list(payload.get("categories")),
        "pricing": pricing,
        "policies": policies,
        "docs": docs,
        "status": status,
        "confidence": _float(payload.get("confidence"), default=0.3),
        "missing_fields": _split_list(payload.get("missing_fields")),
        "source_rank": payload.get("source_rank") or "UNKNOWN",
        "notes": payload.get("notes") or "",
        "curated": True,
        "supplier_verified": False,
    }
    return ActionObject.model_validate(action_object)


def normalize_curated_trace(row: dict[str, Any]) -> SourceTrace:
    payload = dict(row)
    for key in ("trace_id", "object_id", "field", "source_url"):
        if not payload.get(key):
            raise ValueError(f"Curated source trace is missing {key}.")
    payload.setdefault("source_title", payload["source_url"])
    payload.setdefault("source_snippet", "")
    payload.setdefault("retrieved_at", "1970-01-01T00:00:00+00:00")
    payload["confidence"] = _float(payload.get("confidence"), default=0.3)
    payload.setdefault("source_rank", "UNKNOWN")
    return SourceTrace.model_validate(payload)


def load_curated_objects(
    path: str | Path = "data/curated/curated_objects_v0_1.jsonl",
    strict: bool = False,
) -> list[ActionObject]:
    rows, errors = _read_jsonl(path, strict=strict)
    objects: list[ActionObject] = []
    for index, row in enumerate(rows):
        try:
            objects.append(normalize_curated_object(row))
        except Exception as exc:
            errors.append(f"object[{index}]: {exc}")
    if strict and errors:
        raise ValueError("; ".join(errors))
    return objects


def load_curated_source_traces(
    path: str | Path = "data/curated/curated_source_traces_v0_1.jsonl",
    strict: bool = False,
) -> list[SourceTrace]:
    rows, errors = _read_jsonl(path, strict=strict)
    traces: list[SourceTrace] = []
    for index, row in enumerate(rows):
        try:
            traces.append(normalize_curated_trace(row))
        except Exception as exc:
            errors.append(f"trace[{index}]: {exc}")
    if strict and errors:
        raise ValueError("; ".join(errors))
    return traces
