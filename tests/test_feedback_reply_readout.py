from ai_objective_index.portfolio.feedback_reply_intake import package_feedback_replies
from ai_objective_index.portfolio.feedback_reply_readout import build_feedback_reply_readout


def test_readout_includes_claim_boundary():
    bundle = package_feedback_replies(sample=True)
    readout = build_feedback_reply_readout(bundle)
    assert "Not reply sending" in readout
    assert "No external action authorization" in readout
