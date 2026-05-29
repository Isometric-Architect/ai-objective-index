from ai_objective_index.portfolio.qira_pilot_packager import build_qira_pilot_receipt
from ai_objective_index.portfolio.qira_pilot_receipt import to_jsonable
from ai_objective_index.portfolio.qira_reviewer_readout import build_reviewer_readout_markdown


def test_qira_reviewer_readout_includes_claim_boundary():
    text = build_reviewer_readout_markdown(to_jsonable(build_qira_pilot_receipt(sample=True)))

    assert "Not code correctness proof" in text
    assert "No merge authorization" in text
    assert "No deploy authorization" in text
