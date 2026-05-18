from __future__ import annotations

import json
from pathlib import Path

from ai_objective_index.registry_intake.registry_payload_audit import run_registry_payload_audit, save_registry_payload_audit


def test_registry_payload_audit_works_with_fixture() -> None:
    root = Path("data/generated/test_registry_payload_audit_fixture")
    root.mkdir(parents=True, exist_ok=True)
    (root / "mcp_registry_raw_v0_1.json").write_text(
        json.dumps({"fixture_mode": True, "payload": {"servers": [{"name": "io.github.example/x", "fixture_only": True}]}}),
        encoding="utf-8",
    )

    result = run_registry_payload_audit(root)

    assert result["raw_payload_mode"] == "fixture"
    assert result["real_payload_available"] is False


def test_registry_payload_audit_works_with_real_like_files() -> None:
    root = Path("data/generated/test_registry_payload_audit_real")
    root.mkdir(parents=True, exist_ok=True)
    (root / "mcp_registry_raw_v0_1.json").write_text(
        json.dumps({"servers": [{"server": {"name": "ai.real/audit", "version": "1.0.0"}}]}),
        encoding="utf-8",
    )
    (root / "mcp_registry_objects_v0_1.jsonl").write_text("", encoding="utf-8")
    (root / "mcp_registry_source_traces_v0_1.jsonl").write_text("", encoding="utf-8")

    result = run_registry_payload_audit(root)
    path = save_registry_payload_audit(result, root / "registry_payload_audit_v0_1.json")

    assert result["raw_payload_mode"] == "manual_raw"
    assert result["real_payload_available"] is True
    assert result["fixture_leak_detected"] is False
    assert path.exists()


def test_registry_payload_audit_detects_fixture_leak() -> None:
    root = Path("data/generated/test_registry_payload_audit_leak")
    root.mkdir(parents=True, exist_ok=True)
    (root / "mcp_registry_raw_v0_1.json").write_text(
        json.dumps({"servers": [{"server": {"name": "ai.real/leak", "version": "1.0.0"}}]}),
        encoding="utf-8",
    )
    (root / "mcp_registry_objects_v0_1.jsonl").write_text(
        json.dumps({"object_id": "x", "name": "io.github.example/leak", "fixture_only": True}) + "\n",
        encoding="utf-8",
    )

    result = run_registry_payload_audit(root)

    assert result["fixture_leak_detected"] is True
