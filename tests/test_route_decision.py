from ai_objective_index.vnext.evidence_summary import CapabilityEvidenceSummary
from ai_objective_index.vnext.risk_boundary import CapabilityRiskBoundary
from ai_objective_index.vnext.route_decision import decide_route


def test_route_decision_blocks_forbidden_actions():
    decision = decide_route(
        CapabilityEvidenceSummary(source_trace_count=1, source_trace_coverage=0.4, confidence=0.6, evidence_status="SOURCE_TRACED"),
        CapabilityRiskBoundary(forbidden_actions_detected=["payment"], route_block_reasons=["Forbidden action language detected."]),
        [],
    )
    assert decision.decision == "BLOCK_FORBIDDEN_ACTION"


def test_route_decision_blocks_unsupported_claims():
    decision = decide_route(
        CapabilityEvidenceSummary(source_trace_count=1, source_trace_coverage=0.4, confidence=0.6, evidence_status="SOURCE_TRACED"),
        CapabilityRiskBoundary(unsupported_claims_detected=["security certified"], route_block_reasons=["Unsupported claim."]),
        [],
    )
    assert decision.decision == "BLOCK_UNSUPPORTED_CLAIM"


def test_missing_critical_fields_hold():
    decision = decide_route(
        CapabilityEvidenceSummary(source_trace_count=1, source_trace_coverage=0.4, confidence=0.6, evidence_status="SOURCE_TRACED"),
        CapabilityRiskBoundary(),
        ["docs_url"],
    )
    assert decision.decision == "HOLD_MISSING_FIELDS"


def test_source_traced_complete_object_can_allow_candidate_but_not_verify():
    decision = decide_route(
        CapabilityEvidenceSummary(
            source_trace_count=3,
            source_trace_coverage=0.6,
            confidence=0.7,
            evidence_status="OFFICIAL_TRACE_AVAILABLE",
            docs_found=True,
            pricing_found=True,
            policy_found=True,
        ),
        CapabilityRiskBoundary(),
        [],
    )
    assert decision.decision == "ALLOW_CANDIDATE"
    assert "verified" in decision.must_not_claim
