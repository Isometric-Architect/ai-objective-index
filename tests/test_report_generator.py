from ai_objective_index.report_generator import generate_all_reports


def test_generate_all_reports_writes_reports_and_downloads():
    paths = generate_all_reports()
    path_names = {path.as_posix() for path in paths}

    expected_reports = [
        "reports/mcp_server_objective_index_v0_1.md",
        "reports/ai_tool_pricing_index_v0_1.md",
        "reports/source_trace_quality_report_v0_1.md",
    ]
    expected_downloads = [
        "data/downloads/action_objects_v0_1.json",
        "data/downloads/source_traces_v0_1.json",
        "data/downloads/objective_scores_v0_1.json",
        "data/downloads/golden_queries_v0_1.json",
    ]

    for expected in expected_reports + expected_downloads:
        assert any(name.endswith(expected) for name in path_names)

    report_paths = [path for path in paths if path.suffix == ".md" and "reports" in path.parts]
    assert report_paths
    for report_path in report_paths:
        text = report_path.read_text(encoding="utf-8")
        assert "not a quality guarantee" in text

