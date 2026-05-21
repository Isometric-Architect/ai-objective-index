from ai_objective_index import public_private_split_audit as audit


def test_public_private_split_doc_text_passes():
    text = """
Public: schemas, API/MCP shapes, high-level score components, ALLOW/HOLD/BLOCK.
Private: weights, thresholds, anti-gaming, provider trust priors, private negative controls remain private.
"""

    assert audit.scan_text_for_private_split_violations(text) == []


def test_provider_trust_prior_exposure_blocks():
    findings = audit.scan_text_for_private_split_violations("provider trust prior = 0.91")

    assert findings
