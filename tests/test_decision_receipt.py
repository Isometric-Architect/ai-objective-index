from ai_objective_index.decision_receipt import generate_decision_receipt
from ai_objective_index.seed_loader import load_sample_index, load_source_traces
from ai_objective_index.store import ObjectiveIndexStore


def test_creates_receipt_with_known_limits_and_source_trace_ids():
    store = ObjectiveIndexStore(load_sample_index(), load_source_traces())

    receipt = generate_decision_receipt(
        store,
        "aoi-pixelforge-api",
        alternatives=["aoi-motioncanvas-ai", "aoi-embedlite-api"],
        query="cheap image generation API with commercial use terms",
        constraints={"max_monthly_budget_usd": 50},
    )

    assert receipt.selected_object_id == "aoi-pixelforge-api"
    assert "v0.1 read-only benchmark output" in receipt.known_limits
    assert "not a quality guarantee" in receipt.known_limits
    assert "no purchase, booking, payment, login, email, or contract execution" in receipt.known_limits
    assert receipt.source_trace_ids == ["trace-pixelforge-pricing"]

