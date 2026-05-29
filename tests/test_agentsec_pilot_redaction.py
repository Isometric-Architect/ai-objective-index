from ai_objective_index.portfolio.agentsec_pilot_redaction import scan_payload


def test_agentsec_pilot_redaction_passes_safe_payload():
    result = scan_payload({"note": "local/offline manifest review only"})

    assert result["decision"] == "PASS_REDACTED"
    assert result["finding_count"] == 0


def test_agentsec_pilot_redaction_blocks_token_like_string():
    result = scan_payload({"note": "pypi-abcdefghijklmnopqrstuvwxyz123456"})

    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"
    assert result["block_count"] == 1


def test_agentsec_pilot_redaction_blocks_private_kernel_value():
    result = scan_payload({"note": "provider trust prior: 0.91"})

    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"
