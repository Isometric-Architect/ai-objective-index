from ai_objective_index.beta_readiness import build_beta_readiness_report, write_beta_readiness_report


def test_beta_readiness_report_writes_markdown():
    report_path = write_beta_readiness_report()
    text = report_path.read_text(encoding="utf-8")

    assert "PASS" in text or "HOLD" in text or "BLOCK" in text
    assert "No live crawling" in text
    assert "EXTRACTED_UNVERIFIED" in text
    assert "Productization Mode" in text

    markdown, metadata = build_beta_readiness_report()
    assert "Beta Readiness" in markdown
    assert metadata["overall"] in {"PASS", "HOLD"}
