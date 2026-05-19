from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ActionObject, SourceTrace


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate

    root_candidate = _repo_root() / candidate
    if root_candidate.exists():
        return root_candidate

    return root_candidate


def _load_json(path: str | Path) -> dict[str, Any]:
    resolved = _resolve_path(path)
    with resolved.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_sample_index(path: str | Path = "data/sample_index.json") -> list[ActionObject]:
    payload = _load_json(path)
    return [ActionObject.model_validate(item) for item in payload.get("objects", [])]


def load_source_traces(path: str | Path = "data/sample_source_traces.json") -> list[SourceTrace]:
    payload = _load_json(path)
    return [SourceTrace.model_validate(item) for item in payload.get("traces", [])]


def load_golden_queries(path: str | Path = "data/golden_queries.json") -> list[dict[str, Any]]:
    payload = _load_json(path)
    return list(payload.get("queries", []))

