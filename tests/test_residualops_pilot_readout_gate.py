from pathlib import Path

from ai_objective_index.residualops_pilot_feedback_memory import build_feedback_memory, build_pilot_receipt_template
from ai_objective_index.residualops_pilot_readout_gate import (
    PACKAGE_RESULT_PATH,
    SECOND_RUN_GATE_PATH,
    build_pilot_receipt_readout,
    build_second_run_decision_gate,
    run_pilot_readout_gate,
    run_roe7_claim_audit,
)


def test_roe7_readout_gate_ready_without_external_actions():
    result = run_pilot_readout_gate(write_result=True)

    assert result["decision"] == "PASS_ROE7_PILOT_READOUT_GATE_READY"
    assert result["second_run_gate_decision"] == "HOLD_FIRST_PILOT_RECEIPT_REQUIRED"
    assert result["workflow_enabled"] is False
    assert result["github_api_used"] is False
    assert result["token_printed"] is False
    assert Path(PACKAGE_RESULT_PATH).exists()
    assert Path(SECOND_RUN_GATE_PATH).exists()


def test_readout_holds_without_accepted_receipts():
    readout = build_pilot_receipt_readout(
        feedback_memory=build_feedback_memory([]),
        roe6_result={"decision": "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY"},
    )

    assert readout["decision"] == "HOLD_FIRST_PILOT_RECEIPT_REQUIRED"
    assert readout["can_authorize_action"] is False


def test_readout_holds_failure_signals():
    receipt = build_pilot_receipt_template()
    receipt["owner_consent_confirmed"] = True
    receipt["outcome"] = "fail"
    memory = build_feedback_memory([receipt])

    readout = build_pilot_receipt_readout(memory, {"decision": "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY"})

    assert readout["decision"] == "HOLD_FAILURE_REVIEW_REQUIRED"


def test_second_run_gate_requires_owner_consent_and_operator_review():
    receipt = build_pilot_receipt_template()
    receipt["owner_consent_confirmed"] = True
    receipt["outcome"] = "allow"
    memory = build_feedback_memory([receipt])
    readout = build_pilot_receipt_readout(memory, {"decision": "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY"})

    missing_consent = build_second_run_decision_gate(readout)
    missing_review = build_second_run_decision_gate(readout, owner_consent_confirmed=True)
    ready = build_second_run_decision_gate(readout, owner_consent_confirmed=True, operator_review_complete=True)

    assert readout["decision"] == "PASS_READOUT_READY_FOR_SECOND_RUN_GATE"
    assert missing_consent["decision"] == "HOLD_OWNER_CONSENT_REQUIRED_FOR_SECOND_RUN"
    assert missing_review["decision"] == "HOLD_OPERATOR_REVIEW_REQUIRED"
    assert ready["decision"] == "PASS_SECOND_RUN_MANUAL_DRY_RUN_READY"
    assert ready["workflow_enabled_by_aoi"] is False
    assert ready["can_authorize_action"] is False


def test_second_run_gate_does_not_override_failure_hold():
    readout = {"decision": "HOLD_FAILURE_REVIEW_REQUIRED"}
    gate = build_second_run_decision_gate(readout, owner_consent_confirmed=True, operator_review_complete=True)

    assert gate["decision"] == "HOLD_FAILURE_REVIEW_REQUIRED"
    assert gate["can_prepare_manual_second_run"] is False


def test_roe7_claim_audit_blocks_private_kernel_fixture(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("private negative-control seed: never-public\n", encoding="utf-8")

    result = run_roe7_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "BLOCK_ROE7_PRIVATE_KERNEL_LEAK"


def test_roe7_claim_audit_allows_negative_context(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("Do not claim action authorized or security certified status.\n", encoding="utf-8")

    result = run_roe7_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "PASS_ROE7_CLAIM_BOUNDARY"
