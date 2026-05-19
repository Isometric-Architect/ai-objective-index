from __future__ import annotations

from collections import Counter
from typing import Any

from .action_boundary import check_action_boundary, forbidden_actions_v0_1
from .claim_ceiling import claim_ceiling_not_asserted_list


def _result_value(result: dict[str, Any], key: str, default: Any = None) -> Any:
    return result.get(key, default) if isinstance(result, dict) else default


def build_decision_packet(
    query: str,
    results: list[dict[str, Any]],
    objective: str | None = None,
    constraints: dict[str, Any] | None = None,
    data_scope: str = "sample",
) -> dict[str, Any]:
    statuses = Counter(str(_result_value(result, "status", "UNKNOWN")) for result in results)
    trace_ids: list[str] = []
    missing_fields: dict[str, list[str]] = {}
    ceilings: dict[str, str] = {}
    for result in results:
        object_id = str(_result_value(result, "object_id", "unknown"))
        missing_fields[object_id] = list(_result_value(result, "missing_fields", []) or [])
        if _result_value(result, "claim_ceiling"):
            ceilings[object_id] = str(_result_value(result, "claim_ceiling"))
        trace_ids.extend(str(item) for item in (_result_value(result, "source_trace_ids", []) or []))

    return {
        "Q": {
            "query": query,
            "objective": objective,
            "constraints": constraints or {},
        },
        "O": {
            "data_scope": data_scope,
            "source_contract": "source-status before evidence; source traces support fields but do not guarantee completeness",
            "read_only": True,
        },
        "Pi": {
            "process_route": "search/rank/compare/explain",
            "validator_before_claim": True,
        },
        "F": {
            "candidate_count": len(results),
            "candidate_ids": [str(_result_value(result, "object_id", "")) for result in results],
        },
        "R": {
            "missing_fields": missing_fields,
            "residual_warning": "Missing fields remain visible and are not silently closed.",
        },
        "T": {
            "status_counts": dict(statuses),
            "freshness_note": "Stale records require reconfirmation before current-truth claims.",
        },
        "L": {
            "claim_ceilings": ceilings,
            "not_asserted": claim_ceiling_not_asserted_list(next(iter(ceilings.values()), "SAMPLE_BENCHMARK_ONLY")),
            "use_rights": {
                "allowed": ["READ", "RANK", "COMPARE", "QUOTE"],
                "held_or_blocked": ["TRAIN", "SHARE", "MEMORY", "ACTION"],
            },
        },
        "A": {
            "allowed": [
                check_action_boundary("READ"),
                check_action_boundary("RANK"),
                check_action_boundary("COMPARE"),
                check_action_boundary("EXPLAIN"),
                check_action_boundary("DECISION_RECEIPT"),
            ],
            "blocked": forbidden_actions_v0_1(),
        },
        "W": {
            "source_trace_ids": sorted(set(trace_ids)),
            "receipt_ids": [],
            "witness_note": "Decision packet is a read-only packet, not an action license.",
        },
    }
