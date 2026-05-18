from __future__ import annotations

from ai_objective_index.registry_intake.registry_run_receipt import build_registry_run_receipt


def test_registry_run_receipt_has_safety_fields() -> None:
    receipt = build_registry_run_receipt(
        mode="offline",
        allow_network=False,
        base_url="https://registry.modelcontextprotocol.io",
        endpoint="/v0.1/servers?limit=50",
        max_servers=50,
        raw_payload_path="data/registry/mcp_registry_raw_v0_1.json",
        live_network_used=False,
    )

    assert receipt["mode"] == "offline"
    assert receipt["allow_network"] is False
    assert receipt["live_network_used"] is False
    assert receipt["arbitrary_scraping_used"] is False
    assert receipt["credentials_used"] is False
