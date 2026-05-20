from pathlib import Path

from ai_objective_index.vnext.trust_cli import REPORT_PATH, RESULT_PATH, run_trust_cli


def test_trust_cli_runs_offline_and_writes_report():
    report = run_trust_cli(
        query="image API",
        objective="select source-traced API candidates",
        data_scope="sample",
        limit=2,
    )
    assert report["summary"]["candidate_count"] <= 2
    assert Path(REPORT_PATH).exists()
    assert Path(RESULT_PATH).exists()
    result_text = Path(RESULT_PATH).read_text(encoding="utf-8")
    assert '"network_used": false' in result_text
    assert '"pypi_upload_performed": false' in result_text
