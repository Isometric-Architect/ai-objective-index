from __future__ import annotations

import json
from pathlib import Path

from ai_objective_index.registry_intake.real_payload_guard import (
    assert_no_fixture_overwrite,
    detect_payload_mode,
    is_fixture_payload,
    is_real_registry_payload,
    summarize_payload,
)


def _fixture_payload():
    return {
        "fixture_mode": True,
        "payload": {
            "servers": [
                {
                    "name": "io.github.example/browser-automation",
                    "fixture_only": True,
                }
            ]
        },
    }


def _real_payload():
    return {
        "servers": [
                {
                    "server": {
                    "name": "ai.real/candidate-mcp",
                    "description": "Real-like registry metadata",
                    "version": "1.0.0",
                }
            }
        ]
    }


def test_detects_fixture_payload() -> None:
    assert is_fixture_payload(_fixture_payload()) is True
    assert is_real_registry_payload(_fixture_payload()) is False


def test_detects_real_manual_like_payload() -> None:
    payload = _real_payload()

    assert is_fixture_payload(payload) is False
    assert is_real_registry_payload(payload) is True
    assert summarize_payload(payload)["record_count"] == 1


def test_detect_payload_mode_from_path() -> None:
    path = Path("data/generated/test_real_payload_guard_raw.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_real_payload()), encoding="utf-8")

    assert detect_payload_mode(path) == "manual_raw"


def test_prevents_fixture_overwrite_of_real_raw() -> None:
    path = Path("data/generated/test_real_payload_guard_overwrite.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_real_payload()), encoding="utf-8")

    result = assert_no_fixture_overwrite(path, "fixture")

    assert result["blocked"] is True
    assert result["allowed"] is False
