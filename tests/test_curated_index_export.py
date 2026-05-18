from __future__ import annotations

import json

from ai_objective_index.curated_index_export import export_curated_index


def test_curated_index_export_writes_json() -> None:
    payload = export_curated_index()

    from pathlib import Path

    output = Path("data/curated/curated_public_beta_index_v0_1.json")
    validation = Path("data/curated/curated_validation_results_v0_1.json")
    assert output.exists()
    assert validation.exists()
    written = json.loads(output.read_text(encoding="utf-8"))
    assert written["object_count"] == payload["object_count"]
    assert "trace_count" in written
    assert "public_beta_ready_count" in written
