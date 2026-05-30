from ai_objective_index.agent_adoption.agent_claim_boundary import (
    CLAIM_BOUNDARY,
    MUST_NOT_CLAIM,
    scan_text_for_overclaims,
)


def test_claim_boundary_blocks_overclaim_fixture():
    findings = scan_text_for_overclaims("This tool is security certified and production ready.")

    assert any(item["kind"] == "overclaim" for item in findings)


def test_claim_boundary_allows_negated_claim_boundary_context():
    findings = scan_text_for_overclaims("AOI is not security certified and is not production ready.")

    assert findings == []


def test_private_kernel_value_is_blocked():
    findings = scan_text_for_overclaims("ranking weights: 0.91")

    assert any(item["kind"] == "private_kernel_value" for item in findings)


def test_claim_boundary_lists_agent_failure_distinctions():
    joined = " ".join(CLAIM_BOUNDARY)

    assert "tool_available != tool_authorized" in joined
    assert "metadata != proof" in joined
    assert MUST_NOT_CLAIM

