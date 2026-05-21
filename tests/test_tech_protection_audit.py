from ai_objective_index import tech_protection_audit as audit


def test_safe_public_scoring_component_names_pass():
    findings = audit.scan_text_for_sensitive_disclosure("Public high-level component names: objective_fit, freshness, demo_profile_v0_1")

    assert findings == []


def test_exact_private_weight_fixture_triggers_review_or_block():
    findings = audit.scan_text_for_sensitive_disclosure("private ranking weight: 0.73")

    assert findings
    assert findings[0]["severity"] in {"HOLD", "BLOCK"}


def test_token_like_fixture_blocks():
    findings = audit.scan_text_for_sensitive_disclosure("pypi-abcdefghijklmnopqrstuvwxyz123456")

    assert any(item["kind"] == "token_or_secret" for item in findings)


def test_internal_source_master_file_fixture_blocks():
    result = audit.audit_paths(["SOURCE_0513_REPACK_FINAL_v1/private.md"])

    assert result["decision"] == "BLOCK_INTERNAL_SOURCE_LEAK"
