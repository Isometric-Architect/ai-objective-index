from ai_objective_index.portfolio.pilot_dry_run_feedback_memory import build_dry_run_feedback_memory
from ai_objective_index.portfolio.pilot_dry_run_receipt import PilotDryRunReceipt, PilotDryRunResult, PilotDryRunTrace, to_jsonable


def sample_result(vertical: str = "agentsec") -> PilotDryRunResult:
    return PilotDryRunResult(
        dry_run_id="dry-run-1",
        vertical=vertical,  # type: ignore[arg-type]
        intake_id=f"intake-{vertical}",
        selected_packager=f"package_{vertical}_pilot",
        receipt_path=f"pilot_receipts/{vertical}/sample.json",
        gate_result=f"PASS_{vertical.upper()}",
        allow_count=1,
        hold_count=1,
        block_count=1,
        primary_decision="BLOCK_SAMPLE",
        redaction_status="PASS_REDACTED",
    )


def test_dry_run_trace_serializes():
    trace = PilotDryRunTrace(dry_run_id="dry-run-1", intake_ids=["a"], executed_verticals=["agentsec"])
    payload = to_jsonable(trace)
    assert payload["schema"] == "ResidualOps_PilotDryRunTrace/v0.1"
    assert payload["local_only"] is True
    assert payload["github_api_used"] is False


def test_dry_run_receipt_serializes():
    results = [sample_result()]
    receipt = PilotDryRunReceipt(
        dry_run_id="dry-run-1",
        results=results,
        aggregate_summary={
            "vertical_count": 1,
            "total_allow_count": 1,
            "total_hold_count": 1,
            "total_block_count": 1,
            "all_redaction_passed": True,
            "all_gates_passed": True,
            "external_action_count": 0,
        },
        feedback_memory=build_dry_run_feedback_memory("dry-run-1", results),
    )
    payload = to_jsonable(receipt)
    assert payload["schema"] == "ResidualOps_PilotDryRunReceipt/v0.1"
    assert payload["claim_boundary"]["not_external_pilot"] is True
