from __future__ import annotations

from ai_objective_index.registry_intake.registry_beta_dataset_builder import build_registry_beta_dataset
from ai_objective_index.registry_intake.registry_quality_audit import (
    run_registry_quality_audit,
    save_registry_quality_audit,
)


def test_registry_quality_audit_writes_metrics() -> None:
    build_registry_beta_dataset()
    result = run_registry_quality_audit()
    path = save_registry_quality_audit(result)

    assert path.exists()
    assert "source_trace_coverage" in result
    assert "beta_candidate_count" in result
    assert result["live_network_used"] is False
    assert "missing_field_stats" in result
