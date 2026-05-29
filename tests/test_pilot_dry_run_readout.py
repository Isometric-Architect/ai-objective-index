from ai_objective_index.portfolio.pilot_dry_run import build_dry_run_receipt
from ai_objective_index.portfolio.pilot_dry_run_readout import build_dry_run_readout
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


def test_dry_run_readout_includes_claim_boundary():
    receipt = build_dry_run_receipt("dry-run-1", [sample_result("agentsec")])
    text = build_dry_run_readout(receipt)
    assert "Not an external pilot" in text
    assert "No external action authorization" in text
