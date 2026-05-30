from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


VERSION = "0.3.0a2"
PACKAGE_NAME = "ai-objective-index"
MCP_NAME = "io.github.Isometric-Architect/ai-objective-index"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> Path:
    destination = repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def write_text(path: Path, text: str) -> Path:
    destination = repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def read_json(path: Path) -> dict[str, Any]:
    full = repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def read_text(path: Path) -> str:
    full = repo_root() / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")

