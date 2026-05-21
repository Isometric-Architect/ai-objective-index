from pathlib import Path

from ai_objective_index.vnext.execution_receipt_cli_demo import (
    MEMORY_SAMPLE_PATH,
    RESULT_PATH,
    ROUTE_OVERLAY_SAMPLE_PATH,
    run_execution_receipt_cli_demo,
)


def test_execution_receipt_cli_demo_writes_wave6_outputs():
    result = run_execution_receipt_cli_demo(data_scope="sample")
    assert result["external_execution"] is False
    assert result["probe_execution"] is False
    assert Path(RESULT_PATH).exists()
    assert Path(MEMORY_SAMPLE_PATH).exists()
    assert Path(ROUTE_OVERLAY_SAMPLE_PATH).exists()
