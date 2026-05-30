from ai_objective_index.registry_intake.real_payload_guard import (
    detect_payload_mode,
    is_fixture_payload,
    is_real_registry_payload,
    summarize_payload,
)


def _deep_wrapped_payload(depth: int = 80) -> dict:
    payload: dict = {
        "servers": [
            {
                "name": "io.github.real-owner/server",
                "description": "Non-fixture server-shaped payload for recursion regression.",
            }
        ]
    }
    for _ in range(depth):
        payload = {
            "generated_at": "2026-05-30T00:00:00Z",
            "fixture_mode": False,
            "live_network_used": False,
            "source": "official_mcp_registry_api",
            "payload": payload,
        }
    return payload


def test_real_payload_guard_handles_deep_payload_wrappers_without_recursion(tmp_path):
    payload = _deep_wrapped_payload()

    assert is_fixture_payload(payload) is False
    assert is_real_registry_payload(payload) is True
    summary = summarize_payload(payload)
    assert summary["payload_mode"] == "manual_raw"
    assert summary["record_count"] == 1

    target = tmp_path / "mcp_registry_raw_v0_1.json"
    import json

    target.write_text(json.dumps(payload), encoding="utf-8")
    assert detect_payload_mode(target) == "manual_raw"
