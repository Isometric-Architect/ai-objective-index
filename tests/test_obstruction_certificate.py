from ai_objective_index.models import ActionObject
from ai_objective_index.obstruction_certificate import build_obstructions, summarize_obstructions


def _object(**overrides):
    data = {
        "object_id": "obstruction-object",
        "name": "Obstruction Object",
        "object_type": "APIObject",
        "summary": "Local object for obstruction certificate tests.",
        "pricing": {},
        "policies": {},
        "docs": {},
        "status": "EXTRACTED_UNVERIFIED",
        "confidence": 0.4,
    }
    data.update(overrides)
    return ActionObject(**data)


def test_missing_commercial_terms_yields_hold_policy() -> None:
    obstructions = build_obstructions(_object(pricing={"model": "usage", "free_tier": True}), traces=[])
    assert any(item.token == "HOLD_POLICY" for item in obstructions)
    assert all(item.next_action for item in obstructions if item.token.startswith("HOLD_"))


def test_missing_price_yields_hold_price() -> None:
    obstructions = build_obstructions(_object(), traces=[])
    assert any(item.token == "HOLD_PRICE" for item in obstructions)


def test_blocked_action_yields_block_forbidden_action() -> None:
    obstructions = build_obstructions(_object(), traces=[], requested_action="PAY")
    assert any(item.token == "BLOCK_FORBIDDEN_ACTION" for item in obstructions)
    summary = summarize_obstructions(obstructions)
    assert summary["has_block"] is True
