from __future__ import annotations

from ai_objective_index.registry_intake.mcp_registry_export import export_mcp_registry_intake
from ai_objective_index.registry_intake.mcp_registry_report_generator import write_mcp_registry_report


def test_mcp_registry_report_generator_writes_markdown() -> None:
    export_mcp_registry_intake(use_fixture=True, allow_network=False)

    path = write_mcp_registry_report()
    text = path.read_text(encoding="utf-8")

    assert path.exists()
    assert "not a security certification" in text.lower()
    assert "No live crawling" in text
