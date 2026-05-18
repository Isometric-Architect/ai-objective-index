from __future__ import annotations

import json
from pathlib import Path

from ai_objective_index.registry_intake.real_payload_activation import activate_real_payload


def _real_payload():
    return {
        "servers": [
            {
                "server": {
                    "name": "ai.real/activation",
                    "description": "Activation test MCP server metadata.",
                    "repository": {"url": "https://github.com/real/activation"},
                    "version": "1.0.0",
                    "packages": [{"registryType": "npm", "identifier": "@real/activation"}],
                }
            }
        ]
    }


def _fixture_payload():
    return {
        "fixture_mode": True,
        "payload": {"servers": [{"name": "io.github.example/fixture", "fixture_only": True}]},
    }


def test_use_existing_raw_with_real_like_payload_activates() -> None:
    root = Path("data/generated/test_real_payload_activation_real")
    root.mkdir(parents=True, exist_ok=True)
    raw = root / "mcp_registry_raw_v0_1.json"
    raw.write_text(json.dumps(_real_payload()), encoding="utf-8")
    output = root / "activation.json"

    result = activate_real_payload(use_existing_raw=True, raw_target=raw, output_path=output)

    assert result["activated"] is True
    assert result["payload_mode"] == "manual_raw"
    assert result["live_network_used"] is False
    assert output.exists()


def test_fixture_payload_does_not_activate_public_beta() -> None:
    root = Path("data/generated/test_real_payload_activation_fixture")
    root.mkdir(parents=True, exist_ok=True)
    raw = root / "mcp_registry_raw_v0_1.json"
    raw.write_text(json.dumps(_fixture_payload()), encoding="utf-8")

    result = activate_real_payload(use_existing_raw=True, raw_target=raw, output_path=root / "activation.json")

    assert result["activated"] is False
    assert result["payload_mode"] == "fixture"
    assert result["warnings"]


def test_missing_payload_writes_next_action() -> None:
    root = Path("data/generated/test_real_payload_activation_missing")
    root.mkdir(parents=True, exist_ok=True)
    raw = root / "missing_raw.json"
    if raw.exists():
        raw.unlink()

    result = activate_real_payload(use_existing_raw=True, raw_target=raw, output_path=root / "activation.json")

    assert result["activated"] is False
    assert result["payload_mode"] == "missing"
    assert "Download GET /v0.1/servers JSON" in result["next_action"]
