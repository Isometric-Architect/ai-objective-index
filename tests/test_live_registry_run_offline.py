from __future__ import annotations

import shutil
from pathlib import Path

from ai_objective_index.registry_intake.mcp_registry_client import load_raw_registry_fixture
from ai_objective_index.registry_intake.live_registry_run import run_live_registry_intake


def _clean(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def test_live_registry_run_without_network_writes_fallback_status() -> None:
    output_dir = Path("data/registry_live_test_no_raw")
    _clean(output_dir)
    try:
        result = run_live_registry_intake(
            allow_network=False,
            output_dir=output_dir,
            use_manual_raw_if_present=True,
        )

        assert result["mode"] == "offline"
        assert result["live_network_used"] is False
        assert result["success"] is False
        assert (output_dir / "mcp_registry_manual_fallback_status_v0_1.json").exists()
    finally:
        _clean(output_dir)


def test_live_registry_run_processes_manual_raw_without_network() -> None:
    output_dir = Path("data/registry_live_test_manual_raw")
    _clean(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        raw_path = output_dir / "mcp_registry_raw_v0_1.json"
        raw_path.write_text(
            __import__("json").dumps(load_raw_registry_fixture(), indent=2),
            encoding="utf-8",
        )

        result = run_live_registry_intake(
            allow_network=False,
            output_dir=output_dir,
            use_manual_raw_if_present=True,
        )

        assert result["mode"] == "manual_raw"
        assert result["live_network_used"] is False
        assert result["object_count"] >= 5
        assert (output_dir / "mcp_registry_live_run_receipt_v0_1.json").exists()
    finally:
        _clean(output_dir)
