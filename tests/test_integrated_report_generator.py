from pathlib import Path
from uuid import uuid4

from ai_objective_index.integrated_report_generator import generate_integrated_report


def test_integrated_report_generator_writes_markdown() -> None:
    output_path = Path("data/generated") / f"integrated_report_test_{uuid4().hex}.md"
    try:
        path = generate_integrated_report(path=output_path)
        content = path.read_text(encoding="utf-8")

        assert "EXTRACTED_UNVERIFIED" in content
        assert "No live crawling" in content
    finally:
        if output_path.exists():
            output_path.unlink()
