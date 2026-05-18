from __future__ import annotations

import json
from pathlib import Path

from ai_objective_index.registry_intake.mcp_registry_export import export_mcp_registry_intake
from ai_objective_index.registry_intake.mcp_registry_loader import load_registry_objects


def test_offline_fixture_export_writes_registry_outputs() -> None:
    result = export_mcp_registry_intake(use_fixture=True, allow_network=False)

    assert result["live_network_used"] is False
    assert result["fixture_mode"] is True
    assert result["object_count"] >= 5
    assert result["public_beta_ready_count"] == 0

    root = Path("data/registry")
    assert (root / "mcp_registry_objects_v0_1.jsonl").exists()
    assert (root / "mcp_registry_source_traces_v0_1.jsonl").exists()
    assert (root / "mcp_registry_validation_results_v0_1.json").exists()
    public_beta = json.loads((root / "mcp_registry_public_beta_index_v0_1.json").read_text(encoding="utf-8"))
    assert public_beta["public_beta_ready_count"] == 0
    assert public_beta["fixture_mode"] is True

    objects = load_registry_objects()
    assert all(str(item.status) == "EXTRACTED_UNVERIFIED" for item in objects)
    assert all(str(item.status) not in {"VERIFIED", "ACTION_READY"} for item in objects)
