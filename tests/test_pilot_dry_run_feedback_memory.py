from ai_objective_index.portfolio.pilot_dry_run_feedback_memory import build_dry_run_feedback_memory, feedback_memory_to_jsonable
from ai_objective_index.portfolio.pilot_dry_run_receipt import PilotDryRunResult


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


def test_dry_run_feedback_memory_validates():
    memory = build_dry_run_feedback_memory("dry-run-1", [sample_result("qira")])
    payload = feedback_memory_to_jsonable(memory)
    assert payload["schema"] == "ResidualOps_PilotDryRunFeedbackMemory/v0.1"
    assert payload["feedback_status"] == "pending"
    assert payload["vertical_entries"][0]["should_request_owner_artifact"] is True
