from ai_objective_index.portfolio.agentsec_pilot_packager import package_agentsec_pilot
from ai_objective_index.portfolio.agentsec_pilot_readout import build_reviewer_readout_markdown


def test_agentsec_pilot_readout_includes_claim_boundary():
    result = package_agentsec_pilot(sample=True)
    text = build_reviewer_readout_markdown(result["receipt"])

    assert "not security certification" in text
    assert "not a compliance audit" in text
    assert "Live MCP call" in text
