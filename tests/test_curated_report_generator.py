from __future__ import annotations

from ai_objective_index.curated_report_generator import write_curated_report


def test_curated_report_generator_writes_markdown() -> None:
    path = write_curated_report()
    text = path.read_text(encoding="utf-8")

    assert path.exists()
    assert "not supplier verified" in text.lower()
    assert "No live crawling" in text
