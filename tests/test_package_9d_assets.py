import json
from pathlib import Path

from ai_objective_index.vnext_execution_receipt_audit import run_execution_receipt_claim_audit


def test_package_9d_assets_exist():
    required = [
        "docs/vnext/package_9d_execution_receipt_loop_mvp.md",
        "docs/vnext/execution_receipt_loop.md",
        "docs/vnext/execution_receipt_submission.md",
        "docs/vnext/execution_receipt_memory.md",
        "docs/vnext/receipt_route_overlay.md",
        "docs/vnext/execution_receipt_limitations.md",
        "schemas/vnext/execution_receipt_submission.schema.json",
        "schemas/vnext/execution_receipt_validation_result.schema.json",
        "schemas/vnext/capability_receipt_memory.schema.json",
        "schemas/vnext/objective_receipt_summary.schema.json",
        "schemas/vnext/receipt_route_overlay.schema.json",
        "api/vnext/examples/execution_receipt_submit_request.json",
        "api/vnext/examples/execution_receipt_submit_response.json",
    ]
    for path in required:
        assert Path(path).exists(), path


def test_execution_receipt_claim_audit_passes():
    result = run_execution_receipt_claim_audit()
    assert result["overall_token"] == "PASS"
    assert result["risky_phrase_count"] == 0
    payload = json.loads(Path("public_launch/wave6/EXECUTION_RECEIPT_CLAIM_BOUNDARY_AUDIT.json").read_text())
    assert payload["token_printed"] is False
