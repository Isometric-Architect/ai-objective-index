from ai_objective_index.portfolio.pilot_dry_run import run_pilot_dry_run


def test_pilot_dry_run_aggregates_counts():
    result = run_pilot_dry_run(sample=True, write_result=True)
    summary = result["receipt"]["aggregate_summary"]
    assert summary["vertical_count"] == 3
    assert summary["total_allow_count"] == 3
    assert summary["total_hold_count"] == 3
    assert summary["total_block_count"] == 3
    assert summary["external_action_count"] == 0
