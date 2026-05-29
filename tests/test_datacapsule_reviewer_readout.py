from ai_objective_index.portfolio.datacapsule_pilot_packager import build_datacapsule_pilot_receipt
from ai_objective_index.portfolio.datacapsule_pilot_receipt import to_jsonable
from ai_objective_index.portfolio.datacapsule_reviewer_readout import build_reviewer_readout_markdown


def test_datacapsule_reviewer_readout_includes_claim_boundary():
    text = build_reviewer_readout_markdown(to_jsonable(build_datacapsule_pilot_receipt(sample=True)))

    assert "Not a legal opinion" in text
    assert "Not a privacy audit" in text
    assert "No training authorization" in text
    assert "No action authorization" in text
