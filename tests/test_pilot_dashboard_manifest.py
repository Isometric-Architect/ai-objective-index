from ai_objective_index.portfolio.pilot_dashboard_builder import generate_dashboard


def test_dashboard_manifest_and_checksums_generated():
    result = generate_dashboard(write_result=True)
    assert result["manifest"]["artifact_count"] >= 10
    assert result["checksums"]["checksum_count"] >= 7
    assert all(item["sha256"] for item in result["manifest"]["artifacts"])
