from __future__ import annotations

from typing import Any


FRESHNESS_STATUSES = [
    "fresh_enough_for_discovery",
    "stale_review_required",
    "unknown",
]

RUGPULL_DIFF_STATUSES = [
    "not_checked",
    "no_diff_detected",
    "version_drift_detected",
    "suspicious_diff_requires_review",
]


def freshness_fields(
    last_checked_at: str = "2026-05-30T00:00:00Z",
    version_pin: str = "0.3.0a2",
    stale: bool = True,
    rugpull_status: str = "not_checked",
    negative_cache_hit: bool = False,
) -> dict[str, Any]:
    return {
        "freshness_status": "stale_review_required" if stale else "fresh_enough_for_discovery",
        "version_pin": version_pin,
        "last_checked_at": last_checked_at,
        "stale_warning": "Source traces should be refreshed before execution or external-facing recommendation." if stale else "",
        "rugpull_diff_status": rugpull_status,
        "known_negative_cache_hit": negative_cache_hit,
        "recheck_policy": "Recheck on version change, stale trace warning, negative cache hit, or before execution.",
    }


def negative_cache_contract(candidate_id: str, reason: str = "deprecated_or_untrusted_candidate") -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "known_negative_cache_hit": True,
        "reason": reason,
        "permanent_proof": False,
        "recheckable_route_artifact": True,
        "next_action": "Do not use cached negative status as eternal proof; recheck source evidence or choose alternate candidate.",
    }
