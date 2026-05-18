from __future__ import annotations

import json
from pathlib import Path

from ai_objective_index.registry_intake.registry_reprocess_all import run_registry_reprocess_all


def test_registry_reprocess_all_missing_raw_returns_manual_fallback() -> None:
    root = Path("data/generated/test_registry_reprocess_missing")
    root.mkdir(parents=True, exist_ok=True)

    result = run_registry_reprocess_all(raw_path=root / "missing.json", output_path=root / "result.json")

    assert result["success"] is False
    assert result["manual_raw_needed"] is True
    assert "Download GET /v0.1/servers JSON" in result["next_action"]


def test_registry_reprocess_all_fixture_raw_returns_hold() -> None:
    root = Path("data/generated/test_registry_reprocess_fixture")
    root.mkdir(parents=True, exist_ok=True)
    raw = root / "mcp_registry_raw_v0_1.json"
    raw.write_text(
        json.dumps({"fixture_mode": True, "payload": {"servers": [{"name": "io.github.example/x", "fixture_only": True}]}}),
        encoding="utf-8",
    )

    result = run_registry_reprocess_all(raw_path=raw, output_path=root / "result.json")

    assert result["success"] is True
    assert result["payload_mode"] == "fixture"
    assert result["manual_raw_needed"] is True
    assert result["public_beta_mcp_count"] == 0


def test_registry_reprocess_all_real_like_raw_triggers_chain(monkeypatch) -> None:
    root = Path("data/generated/test_registry_reprocess_real")
    root.mkdir(parents=True, exist_ok=True)
    raw = root / "mcp_registry_raw_v0_1.json"
    raw.write_text(
        json.dumps({"servers": [{"server": {"name": "ai.real/reprocess", "version": "1.0.0", "description": "Real-like metadata"}}]}),
        encoding="utf-8",
    )

    import ai_objective_index.registry_intake.registry_reprocess_all as module

    monkeypatch.setattr(module, "export_mcp_registry_intake", lambda **kwargs: {"object_count": 1, "trace_count": 1, "warnings": [], "fixture_mode": False})
    monkeypatch.setattr(module, "run_mcp_registry_eval", lambda: {"query_count": 1, "result_count": 1, "fixture_only": False})
    monkeypatch.setattr(module, "save_mcp_registry_eval", lambda payload: root / "eval.json")
    monkeypatch.setattr(module, "write_mcp_registry_report", lambda: root / "report.md")
    monkeypatch.setattr(module, "build_registry_beta_dataset", lambda: {"beta_candidate_count": 1})
    monkeypatch.setattr(module, "run_registry_quality_audit", lambda: {"source_trace_coverage": 1.0, "object_count": 1, "trace_count": 1})
    monkeypatch.setattr(module, "save_registry_quality_audit", lambda payload: root / "quality.json")
    monkeypatch.setattr(module, "write_registry_beta_report", lambda: root / "beta.md")
    monkeypatch.setattr(module, "run_registry_payload_audit", lambda: {"fixture_leak_detected": False, "public_beta_mcp_count": 1})
    monkeypatch.setattr(module, "save_registry_payload_audit", lambda payload: root / "audit.json")
    monkeypatch.setattr(module, "run_datascope_qa", lambda: {"summary": {}})
    monkeypatch.setattr(module, "save_datascope_qa_results", lambda payload: root / "datascope.json")
    monkeypatch.setattr(module, "write_beta_readiness_report", lambda: root / "beta_readiness.md")
    monkeypatch.setattr(module, "run_release_readiness", lambda: {"overall_token": "PASS"})
    monkeypatch.setattr(module, "save_release_readiness", lambda payload: root / "release.json")
    monkeypatch.setattr(module, "export_openapi", lambda: root / "openapi.json")
    monkeypatch.setattr(module, "save_mcp_tool_manifest", lambda: root / "manifest.json")

    result = run_registry_reprocess_all(raw_path=raw, output_path=root / "result.json")

    assert result["success"] is True
    assert result["payload_mode"] == "manual_raw"
    assert result["public_beta_mcp_count"] == 1
    assert result["live_network_used"] is False
