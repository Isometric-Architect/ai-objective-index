from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ActionObject, ObjectStatus, ObjectType, SourceTrace


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _load_json(path: str | Path) -> Any:
    resolved = _resolve_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Generated data file not found: {resolved}")
    try:
        return json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Generated data file is not valid JSON: {resolved}") from exc


def _records(payload: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        value = payload.get(key, payload.get("records", []))
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    raise ValueError(f"Generated payload must contain a list of {key}.")


def normalize_generated_object(raw: dict[str, Any]) -> ActionObject:
    if not isinstance(raw, dict):
        raise ValueError("Generated object must be a JSON object.")
    if not raw.get("object_id"):
        raise ValueError("Generated object is missing object_id.")

    payload = dict(raw)
    payload.setdefault("name", payload["object_id"])
    payload.setdefault("object_type", ObjectType.ToolObject)
    payload.setdefault("summary", "Generated extracted object with unverified fixture status.")
    payload.setdefault("official_url", None)
    payload.setdefault("source_urls", [])
    payload.setdefault("capabilities", [])
    payload.setdefault("categories", ["generated_extraction"])
    payload.setdefault("pricing", {})
    payload.setdefault("policies", {})
    payload.setdefault("docs", {})
    payload.setdefault("confidence", 0.3)
    payload.setdefault("missing_fields", [])
    payload.setdefault("source_rank", "UNKNOWN")
    payload.setdefault("status", ObjectStatus.EXTRACTED_UNVERIFIED)

    return ActionObject.model_validate(payload)


def normalize_generated_trace(raw: dict[str, Any]) -> SourceTrace:
    if not isinstance(raw, dict):
        raise ValueError("Generated source trace must be a JSON object.")
    for field in ("trace_id", "object_id", "field", "source_url"):
        if not raw.get(field):
            raise ValueError(f"Generated source trace is missing {field}.")

    payload = dict(raw)
    payload.setdefault("source_title", payload["source_url"])
    payload.setdefault("source_snippet", "")
    payload.setdefault("retrieved_at", payload.get("extracted_at") or payload.get("last_checked_at") or "1970-01-01T00:00:00+00:00")
    payload.setdefault("confidence", 0.3)
    payload.setdefault("source_rank", "UNKNOWN")
    return SourceTrace.model_validate(payload)


def load_generated_objects(
    path: str | Path = "data/generated/extracted_objects_v0_2.json",
) -> list[ActionObject]:
    payload = _load_json(path)
    objects = []
    errors = []
    for index, record in enumerate(_records(payload, "objects")):
        try:
            objects.append(normalize_generated_object(record))
        except Exception as exc:
            errors.append(f"object[{index}]: {exc}")
    if errors:
        raise ValueError("Generated object validation failed: " + "; ".join(errors))
    return objects


def load_generated_source_traces(
    path: str | Path = "data/generated/extracted_source_traces_v0_2.json",
) -> list[SourceTrace]:
    payload = _load_json(path)
    traces = []
    errors = []
    for index, record in enumerate(_records(payload, "traces")):
        try:
            traces.append(normalize_generated_trace(record))
        except Exception as exc:
            errors.append(f"trace[{index}]: {exc}")
    if errors:
        raise ValueError("Generated source trace validation failed: " + "; ".join(errors))
    return traces

