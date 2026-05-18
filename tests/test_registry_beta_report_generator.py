from __future__ import annotations

from ai_objective_index.registry_intake.registry_beta_report_generator import write_registry_beta_report


def test_registry_beta_report_generator_writes_markdown() -> None:
    path = write_registry_beta_report()
    text = path.read_text(encoding="utf-8").lower()

    assert path.exists()
    assert "not a security certification" in text
    assert "not supplier verified" in text
    assert "candidate count" in text
