from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .action_boundary import check_action_boundary, forbidden_actions_v0_1
from .claim_ceiling import claim_ceiling_not_asserted_list, infer_claim_ceiling
from .models import ActionObject
from .obstruction_certificate import build_obstructions
from .source_governance import can_promote_field, source_status_before_evidence
from .use_rights import check_use_right


DEFAULT_CONTROL_PATH = Path("data/negative_controls/false_closure_controls_v0_2.jsonl")
DEFAULT_RESULT_PATH = Path("data/negative_controls/false_closure_results_v0_2.json")


def _read_jsonl(path: str | Path = DEFAULT_CONTROL_PATH) -> list[dict[str, Any]]:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Negative control file not found: {resolved}")
    rows: list[dict[str, Any]] = []
    for line in resolved.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _minimal_object(**overrides: Any) -> ActionObject:
    base = {
        "object_id": "negative-control-object",
        "name": "Negative Control Object",
        "object_type": "APIObject",
        "summary": "Local negative-control object used to prevent false closure.",
        "official_url": "https://example.com/negative-control",
        "source_urls": ["https://example.com/negative-control"],
        "capabilities": ["api_access"],
        "categories": ["sample"],
        "pricing": {},
        "policies": {},
        "docs": {},
        "status": "UNVERIFIED",
        "confidence": 0.4,
        "missing_fields": [],
    }
    base.update(overrides)
    return ActionObject(**base)


def _evaluate_control(control: dict[str, Any]) -> dict[str, Any]:
    control_type = control["control_type"]
    false_box = False
    forbidden_promotion = False
    blocked_action_blocked = True
    hold_next_action = True
    notes: list[str] = []

    if control_type == "missing_pricing":
        obj = _minimal_object(policies={"commercial_use": "unknown"})
        obstructions = build_obstructions(obj, traces=[])
        false_box = not any(item.token == "HOLD_PRICE" for item in obstructions)
        hold_next_action = all(item.next_action for item in obstructions if item.token.startswith("HOLD_"))
        notes = [item.token for item in obstructions]
    elif control_type == "missing_commercial_terms":
        obj = _minimal_object(pricing={"model": "usage", "free_tier": True})
        obstructions = build_obstructions(obj, traces=[])
        false_box = not any(item.token == "HOLD_POLICY" for item in obstructions)
        hold_next_action = all(item.next_action for item in obstructions if item.token.startswith("HOLD_"))
        notes = [item.token for item in obstructions]
    elif control_type == "source_url_presence":
        result = source_status_before_evidence(
            {
                "field": "pricing",
                "source_url": "https://example.com/pricing",
                "source_title": "Example pricing",
                "confidence": 0.1,
                "status": "UNVERIFIED",
            }
        )
        false_box = result["source_supported"] is True
        forbidden_promotion = result["promotion_decision"] == "ALLOW_INTERNAL_READOUT"
        notes = [result["promotion_decision"]]
    elif control_type == "generated_verified":
        decision = can_promote_field("status", "GENERATED", 0.95, "EXTRACTED_UNVERIFIED")
        forbidden_promotion = decision == "ALLOW_INTERNAL_READOUT"
        false_box = forbidden_promotion
        notes = [str(decision.value if hasattr(decision, "value") else decision)]
    elif control_type == "read_to_train_share_action":
        obj = _minimal_object(status="EXTRACTED_UNVERIFIED")
        checks = [check_use_right(obj, right) for right in ("TRAIN", "SHARE", "ACTION")]
        false_box = any(item["decision"] == "ALLOW" for item in checks)
        notes = [f"{item['use_right']}={item['decision']}" for item in checks]
    elif control_type == "stale_current_truth":
        decision = can_promote_field("pricing", "OFFICIAL_PRICING", 0.95, "STALE")
        false_box = decision == "ALLOW_INTERNAL_READOUT"
        notes = [str(decision.value if hasattr(decision, "value") else decision)]
    elif control_type == "sample_live_crawl":
        obj = _minimal_object(status="EXTRACTED_UNVERIFIED", categories=["sample"])
        false_box = infer_claim_ceiling(obj).value not in {"EXTRACTED_UNVERIFIED", "SAMPLE_BENCHMARK_ONLY"}
        notes = [infer_claim_ceiling(obj).value]
    elif control_type == "score_quality_guarantee":
        not_asserted = claim_ceiling_not_asserted_list("SOURCE_TRACED_READOUT")
        false_box = "not a quality guarantee" not in not_asserted
        notes = not_asserted
    elif control_type == "mcp_write_actions":
        blocked = [check_action_boundary(action) for action in ("PAY", "BOOK", "LOGIN", "EMAIL", "PURCHASE", "SIGN_CONTRACT")]
        blocked_action_blocked = all(item["decision"] == "BLOCK" for item in blocked)
        false_box = not blocked_action_blocked or not forbidden_actions_v0_1()
        notes = [f"{item['action']}={item['decision']}" for item in blocked]
    elif control_type == "hold_next_action":
        obj = _minimal_object()
        obstructions = build_obstructions(obj, traces=[], requested_action="PAY")
        hold_next_action = all(item.next_action for item in obstructions if item.token.startswith("HOLD_"))
        false_box = not hold_next_action
        notes = [item.next_action for item in obstructions]
    else:
        false_box = True
        notes = [f"Unknown control_type: {control_type}"]

    passed = not false_box and not forbidden_promotion and blocked_action_blocked and hold_next_action
    return {
        "control_id": control["control_id"],
        "control_type": control_type,
        "passed": passed,
        "false_BOX": int(false_box),
        "forbidden_promotion": int(forbidden_promotion),
        "blocked_actions_blocked": blocked_action_blocked,
        "hold_next_action": hold_next_action,
        "notes": notes,
    }


def run_false_closure_controls(path: str | Path = DEFAULT_CONTROL_PATH) -> dict[str, Any]:
    controls = _read_jsonl(path)
    results = [_evaluate_control(control) for control in controls]
    false_box = sum(item["false_BOX"] for item in results)
    forbidden_promotions = sum(item["forbidden_promotion"] for item in results)
    blocked_actions_blocked = all(item["blocked_actions_blocked"] for item in results)
    every_hold_has_next_action = all(item["hold_next_action"] for item in results)
    return {
        "control_count": len(results),
        "false_BOX": false_box,
        "forbidden_promotions": forbidden_promotions,
        "blocked_actions_blocked": blocked_actions_blocked,
        "every_hold_has_next_action": every_hold_has_next_action,
        "pass": false_box == 0
        and forbidden_promotions == 0
        and blocked_actions_blocked
        and every_hold_has_next_action,
        "results": results,
    }


def save_false_closure_results(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_RESULT_PATH,
) -> None:
    payload = results or run_false_closure_controls()
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    results = run_false_closure_controls()
    save_false_closure_results(results)
    print(
        "False closure controls: "
        f"pass={results['pass']} "
        f"control_count={results['control_count']} "
        f"false_BOX={results['false_BOX']} "
        f"forbidden_promotions={results['forbidden_promotions']}"
    )


if __name__ == "__main__":
    main()
