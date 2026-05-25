from pathlib import Path

from ai_objective_index.residualops_pilot_feedback_memory import (
    FEEDBACK_MEMORY_PATH,
    PACKAGE_RESULT_PATH,
    build_feedback_memory,
    build_pilot_receipt_template,
    run_pilot_feedback_memory,
    run_roe6_claim_audit,
    validate_pilot_receipt,
)


def test_roe6_feedback_memory_ready_without_external_actions():
    result = run_pilot_feedback_memory(write_result=True)

    assert result["decision"] == "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY"
    assert result["feedback_memory_decision"] == "HOLD_NO_PILOT_RECEIPTS_YET"
    assert result["workflow_enabled"] is False
    assert result["github_api_used"] is False
    assert result["token_printed"] is False
    assert Path(PACKAGE_RESULT_PATH).exists()
    assert Path(FEEDBACK_MEMORY_PATH).exists()


def test_pilot_receipt_template_holds_owner_consent():
    template = build_pilot_receipt_template()
    result = validate_pilot_receipt(template)

    assert template["vertical_id"] == "agentsec"
    assert result["decision"] == "HOLD_OWNER_CONSENT_MISSING"
    assert result["can_enable_workflow"] is False
    assert result["can_certify_security"] is False


def test_validate_receipt_accepts_owner_consented_fixture():
    receipt = build_pilot_receipt_template()
    receipt["receipt_id"] = "fixture-receipt-1"
    receipt["owner_consent_confirmed"] = True
    receipt["outcome"] = "hold"

    result = validate_pilot_receipt(receipt)

    assert result["decision"] == "RECEIPT_ACCEPTED"
    assert result["can_influence_memory"] is True
    assert result["can_authorize_action"] is False


def test_validate_receipt_blocks_token_like_string():
    receipt = build_pilot_receipt_template()
    receipt["owner_consent_confirmed"] = True
    receipt["feedback_notes"] = "do not store pypi-abcdefghijklmnopqrstuvwxyz123456"

    result = validate_pilot_receipt(receipt)

    assert result["decision"] == "BLOCK_TOKEN_OR_SECRET_FINDING"
    assert "[redacted]" in result["sanitized_receipt"]["feedback_notes"]


def test_validate_receipt_blocks_overclaim():
    receipt = build_pilot_receipt_template()
    receipt["owner_consent_confirmed"] = True
    receipt["feedback_notes"] = "verified capability for production users"

    result = validate_pilot_receipt(receipt)

    assert result["decision"] == "BLOCK_OVERCLAIM"


def test_feedback_memory_summarizes_accepted_receipts():
    receipt = build_pilot_receipt_template()
    receipt["owner_consent_confirmed"] = True
    receipt["outcome"] = "fail"
    receipt["hold_reasons"] = ["policy unclear"]
    receipt["block_reasons"] = ["unsupported claim"]
    receipt["missing_inputs"] = ["manifest"]

    memory = build_feedback_memory([receipt])

    assert memory["decision"] == "HOLD_REVIEW_FAILURE_SIGNALS"
    assert memory["receipt_count"] == 1
    assert memory["outcome_counts"]["fail"] == 1
    assert memory["can_upgrade_to_verified"] is False


def test_roe6_claim_audit_blocks_private_kernel_fixture(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("provider trust prior: 0.91\n", encoding="utf-8")

    result = run_roe6_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "BLOCK_ROE6_PRIVATE_KERNEL_LEAK"


def test_roe6_claim_audit_allows_negative_context(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("Do not claim security certified or quality guaranteed status.\n", encoding="utf-8")

    result = run_roe6_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "PASS_ROE6_CLAIM_BOUNDARY"
