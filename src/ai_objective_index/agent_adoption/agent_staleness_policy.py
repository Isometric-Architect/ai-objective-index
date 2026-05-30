from __future__ import annotations

from typing import Any


def build_staleness_policy() -> dict[str, Any]:
    return {
        "schema": "AOI_AgentFreshnessAndStalenessPolicy/v0.1",
        "fields": [
            "last_checked_at",
            "source_trace_age",
            "registry_payload_version",
            "stale_warning",
            "needs_refresh",
            "refresh_next_action",
        ],
        "rules": [
            "Do not claim live freshness unless a live check was actually performed.",
            "Older source traces can still support candidate discovery, but preflight should surface stale_warning.",
            "If metadata age or registry payload version is unclear, use HOLD_STALE_METADATA with a refresh next action.",
            "Freshness supports routing context; it does not verify provider claims or authorize tool execution.",
        ],
        "sample_freshness": {
            "last_checked_at": "2026-05-30T00:00:00Z",
            "source_trace_age": "sample_static_fixture",
            "registry_payload_version": "local_sample_v0_1",
            "stale_warning": "sample data is static and should be refreshed before external use",
            "needs_refresh": True,
            "refresh_next_action": "refresh source traces or keep candidate in HOLD_STALE_METADATA before recommending external use",
            "live_check_performed": False,
        },
    }


def freshness_for_sample(needs_refresh: bool = True) -> dict[str, Any]:
    sample = build_staleness_policy()["sample_freshness"].copy()
    sample["needs_refresh"] = needs_refresh
    if not needs_refresh:
        sample["stale_warning"] = "freshness acceptable for local sample demonstration only"
    return sample

