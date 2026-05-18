from ai_objective_index.decision_packet import build_decision_packet


def test_packet_includes_required_keys() -> None:
    packet = build_decision_packet(
        query="cheap image generation API",
        objective="commercial use",
        constraints={"budget_max": 50},
        results=[
            {
                "object_id": "aoi-test",
                "status": "EXTRACTED_UNVERIFIED",
                "missing_fields": ["rate_limits"],
                "source_trace_ids": ["trace-aoi-test"],
                "claim_ceiling": "EXTRACTED_UNVERIFIED",
            }
        ],
    )
    assert set(packet) == {"Q", "O", "Pi", "F", "R", "T", "L", "A", "W"}
    assert packet["W"]["source_trace_ids"] == ["trace-aoi-test"]
