from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack
from ai_objective_index.portfolio.external_share_pack_redaction import scan_share_payload


def test_external_share_pack_redaction_passes():
    result = generate_external_share_pack(write_result=True)
    assert result["redaction"]["decision"] == "PASS_REDACTED"


def test_external_share_pack_redaction_blocks_token():
    result = scan_share_payload("ghp_" + "a" * 24)
    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"
