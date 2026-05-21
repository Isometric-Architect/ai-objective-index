from pathlib import Path

from ai_objective_index.vnext.probe_cli_demo import run_probe_cli_demo


def test_probe_cli_demo_writes_wave7_outputs():
    result = run_probe_cli_demo("image API", "select source-traced candidates", data_scope="sample", limit=1)
    assert result["network_used"] is False
    assert result["negative_control_false_pass_count"] == 0
    assert Path("public_launch/wave7/PROBE_PLAN_SAMPLE.json").exists()
    assert Path("public_launch/wave7/PROBE_ROUTE_OVERLAY_SAMPLE.json").exists()
