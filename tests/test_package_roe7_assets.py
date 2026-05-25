from pathlib import Path

from ai_objective_index.residualops_pilot_readout_gate import run_pilot_readout_gate


ROOT = Path(__file__).resolve().parents[1]


def test_roe7_docs_exist():
    for relative in [
        "docs/roe7_pilot_readout_second_run_gate.md",
        "docs/residualops_second_run_decision_gate.md",
        "docs/residualops_pilot_readout_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe7_outputs_exist_after_generation():
    run_pilot_readout_gate(write_result=True)

    for relative in [
        "public_launch/roe7/ROE7_PILOT_READOUT_GATE_RESULT.json",
        "public_launch/roe7/ROE7_PILOT_RECEIPT_READOUT.json",
        "public_launch/roe7/ROE7_SECOND_RUN_DECISION_GATE.json",
        "public_launch/roe7/ROE7_OPERATOR_REVIEW_PACKET.md",
        "public_launch/roe7/ROE7_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/roe7/ROE7_ARTIFACT_MANIFEST.json",
        "public_launch/roe7/ROE7_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe7_operator_packet_is_public_safe():
    run_pilot_readout_gate(write_result=True)
    text = (ROOT / "public_launch/roe7/ROE7_OPERATOR_REVIEW_PACKET.md").read_text(encoding="utf-8")

    assert "Second-run gate decision" in text
    assert "not verification" in text
