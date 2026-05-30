from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from .mcp_registry_loader import detect_registry_payload_shape, normalize_registry_records


PayloadMode = Literal["missing", "fixture", "manual_raw", "live_raw", "unknown"]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False).lower()
    except (RecursionError, TypeError):
        return str(value).lower()


def _payload_layers(raw: Any, max_depth: int = 2048) -> list[Any]:
    layers: list[Any] = []
    current = raw
    seen: set[int] = set()
    for _ in range(max_depth):
        layers.append(current)
        if not isinstance(current, dict):
            break
        payload = current.get("payload")
        if payload is None:
            break
        marker = id(payload)
        if marker in seen or payload is current:
            break
        seen.add(marker)
        current = payload
    return layers


def _terminal_payload(raw: Any) -> Any:
    layers = _payload_layers(raw)
    return layers[-1] if layers else raw


def _metadata_without_payload(raw: Any) -> Any:
    if not isinstance(raw, dict):
        return raw
    return {key: value for key, value in raw.items() if key != "payload"}


def is_fixture_payload(raw: Any) -> bool:
    if not raw:
        return False
    markers = (
        '"fixture_mode": true',
        '"fixture_only": true',
        "fixture/sample records",
        "local_fixture_resembling_official_mcp_registry_payload",
        "io.github.example/",
        "github.com/example/",
        "@example/",
    )
    for layer in _payload_layers(raw):
        text = _as_text(_metadata_without_payload(layer))
        if any(marker in text for marker in markers):
            return True
    return False


def is_real_registry_payload(raw: Any) -> bool:
    if not raw or is_fixture_payload(raw):
        return False
    records = normalize_registry_records(_terminal_payload(raw), max_servers=1000)
    if not records:
        return False
    for record in records:
        body = record.get("server") if isinstance(record.get("server"), dict) else record
        name = str(
            body.get("name")
            or body.get("serverName")
            or body.get("server_name")
            or body.get("id")
            or ""
        )
        if name and "example" not in name.lower():
            return True
    return False


def detect_payload_mode(
    path: str | Path = "data/registry/mcp_registry_raw_v0_1.json",
) -> PayloadMode:
    resolved = _resolve(path)
    if not resolved.exists():
        return "missing"
    try:
        raw = _load_json(resolved)
    except json.JSONDecodeError:
        return "unknown"
    if is_fixture_payload(raw):
        return "fixture"
    if is_real_registry_payload(raw):
        if isinstance(raw, dict) and raw.get("live_network_used") is True:
            return "live_raw"
        if isinstance(raw, dict) and raw.get("source") == "official_mcp_registry_api" and raw.get("live_network_used") is True:
            return "live_raw"
        return "manual_raw"
    return "unknown"


def assert_no_fixture_overwrite(
    target_path: str | Path,
    source_mode: str,
) -> dict[str, Any]:
    resolved = _resolve(target_path)
    target_mode = detect_payload_mode(resolved)
    is_blocked = source_mode.lower() in {"fixture", "fixture_only"} and target_mode in {"manual_raw", "live_raw"}
    return {
        "target_path": str(resolved),
        "source_mode": source_mode,
        "target_mode": target_mode,
        "allowed": not is_blocked,
        "blocked": is_blocked,
        "reason": (
            "Refusing to overwrite real/manual MCP Registry raw payload with fixture data."
            if is_blocked
            else "No fixture overwrite risk detected."
        ),
    }


def summarize_payload(raw: Any) -> dict[str, Any]:
    terminal = _terminal_payload(raw)
    records = normalize_registry_records(terminal, max_servers=1000)
    shape = detect_registry_payload_shape(terminal)
    mode: PayloadMode
    if is_fixture_payload(raw):
        mode = "fixture"
    elif is_real_registry_payload(raw):
        mode = "live_raw" if isinstance(raw, dict) and raw.get("live_network_used") is True else "manual_raw"
    else:
        mode = "unknown"
    return {
        "payload_mode": mode,
        "shape": shape.get("shape"),
        "record_count": len(records),
        "record_key": shape.get("record_key"),
        "fixture_payload": is_fixture_payload(raw),
        "real_registry_payload": is_real_registry_payload(raw),
        "live_network_used": bool(raw.get("live_network_used")) if isinstance(raw, dict) else False,
        "source": raw.get("source") if isinstance(raw, dict) else None,
    }


def summarize_payload_path(path: str | Path = "data/registry/mcp_registry_raw_v0_1.json") -> dict[str, Any]:
    resolved = _resolve(path)
    if not resolved.exists():
        return {
            "payload_mode": "missing",
            "path": str(resolved),
            "record_count": 0,
            "fixture_payload": False,
            "real_registry_payload": False,
        }
    try:
        summary = summarize_payload(_load_json(resolved))
    except json.JSONDecodeError as exc:
        return {
            "payload_mode": "unknown",
            "path": str(resolved),
            "record_count": 0,
            "fixture_payload": False,
            "real_registry_payload": False,
            "error": f"Invalid JSON: {exc}",
        }
    summary["path"] = str(resolved)
    return summary
