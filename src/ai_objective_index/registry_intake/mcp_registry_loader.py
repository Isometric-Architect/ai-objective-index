from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.models import ActionObject, SourceTrace


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def load_registry_raw(
    path: str | Path = "data/registry/mcp_registry_raw_v0_1.json",
    fallback_fixture: bool = True,
) -> dict[str, Any]:
    resolved = _resolve(path)
    if resolved.exists():
        return json.loads(resolved.read_text(encoding="utf-8"))
    if fallback_fixture:
        fixture = _resolve("data/registry/mcp_registry_raw_fixture_v0_1.json")
        if fixture.exists():
            return json.loads(fixture.read_text(encoding="utf-8"))
    return {"servers": [], "warning": f"Registry raw file not found: {resolved}"}


def detect_registry_payload_shape(raw: Any) -> dict[str, Any]:
    if isinstance(raw, list):
        return {"shape": "list", "record_count": len(raw), "record_key": None}
    if isinstance(raw, dict):
        for key in ("servers", "items", "data"):
            if isinstance(raw.get(key), list):
                return {"shape": f"object.{key}", "record_count": len(raw[key]), "record_key": key}
        if isinstance(raw.get("payload"), dict):
            return detect_registry_payload_shape(raw["payload"])
        if isinstance(raw.get("payload"), list):
            return {"shape": "object.payload", "record_count": len(raw["payload"]), "record_key": "payload"}
    return {"shape": "unknown", "record_count": 0, "record_key": None}


def normalize_registry_records(raw: Any, max_servers: int | None = None) -> list[dict[str, Any]]:
    records: list[Any]
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict):
        if isinstance(raw.get("payload"), (dict, list)):
            return normalize_registry_records(raw["payload"], max_servers=max_servers)
        records = []
        for key in ("servers", "items", "data"):
            if isinstance(raw.get(key), list):
                records = raw[key]
                break
    else:
        records = []
    normalized = [dict(item) for item in records if isinstance(item, dict)]
    if max_servers is not None:
        normalized = normalized[: max(0, max_servers)]
    return normalized


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    resolved = _resolve(path)
    if not resolved.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in resolved.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            rows.append(item)
    return rows


def load_registry_objects(
    path: str | Path = "data/registry/mcp_registry_objects_v0_1.jsonl",
) -> list[ActionObject]:
    return [ActionObject.model_validate(item) for item in _read_jsonl(path)]


def load_registry_source_traces(
    path: str | Path = "data/registry/mcp_registry_source_traces_v0_1.jsonl",
) -> list[SourceTrace]:
    return [SourceTrace.model_validate(item) for item in _read_jsonl(path)]

