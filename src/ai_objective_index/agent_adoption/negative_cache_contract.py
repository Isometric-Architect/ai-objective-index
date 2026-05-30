from __future__ import annotations

from typing import Any

from .freshness_policy import negative_cache_contract as build_negative_cache_contract


def sample_negative_cache_contract() -> dict[str, Any]:
    return build_negative_cache_contract("sample-stale-tool", "known deprecated fixture candidate")
