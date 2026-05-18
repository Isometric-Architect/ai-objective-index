from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


DEFAULT_RECEIPT_PATH = Path("data/registry/mcp_registry_live_run_receipt_v0_1.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def build_registry_run_receipt(
    mode: str,
    allow_network: bool,
    base_url: str,
    endpoint: str,
    max_servers: int,
    raw_payload_path: str,
    object_count: int = 0,
    trace_count: int = 0,
    public_beta_ready_count: int = 0,
    live_network_used: bool = False,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    next_action: str = "Review registry intake outputs and source traces.",
) -> dict[str, Any]:
    return {
        "run_id": f"mcp-registry-{uuid4()}",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "allow_network": allow_network,
        "base_url": base_url,
        "endpoint": endpoint,
        "max_servers": max_servers,
        "raw_payload_path": raw_payload_path,
        "object_count": object_count,
        "trace_count": trace_count,
        "public_beta_ready_count": public_beta_ready_count,
        "live_network_used": live_network_used,
        "arbitrary_scraping_used": False,
        "link_following_used": False,
        "credentials_used": False,
        "errors": errors or [],
        "warnings": warnings or [],
        "next_action": next_action,
    }


def write_registry_run_receipt(
    receipt: dict[str, Any],
    path: str | Path = DEFAULT_RECEIPT_PATH,
) -> Path:
    destination = _resolve(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination

