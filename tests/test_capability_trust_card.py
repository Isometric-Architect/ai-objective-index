from ai_objective_index.models import ActionObject, SourceTrace
from ai_objective_index.vnext.capability_adapter import build_capability_trust_card, objective_request_to_objective_card


def _object() -> ActionObject:
    return ActionObject(
        object_id="cap-browser",
        name="Browser MCP Candidate",
        object_type="MCPServer",
        summary="Source-traced browser automation MCP server candidate.",
        official_url="https://example.com/browser",
        source_urls=["https://github.com/example/browser-mcp"],
        capabilities=["browser automation", "mcp"],
        categories=["mcp_servers"],
        pricing={"model": "free"},
        policies={"commercial_use": "allowed", "privacy_url": "https://example.com/privacy", "data_retention": "unknown"},
        docs={"docs_url": "https://example.com/docs"},
        status="EXTRACTED_UNVERIFIED",
        confidence=0.7,
    )


def _trace() -> SourceTrace:
    return SourceTrace(
        trace_id="trace-browser-docs",
        object_id="cap-browser",
        field="docs.docs_url",
        source_url="https://example.com/docs",
        source_title="Docs",
        source_snippet="Browser automation docs.",
        retrieved_at="2026-05-21T00:00:00Z",
        confidence=0.8,
        source_rank="A",
    )


def test_capability_trust_card_serializes_to_json():
    objective = objective_request_to_objective_card(
        query="browser automation MCP server",
        objective="select source-traced MCP candidates",
        domain="mcp_servers",
    )
    card = build_capability_trust_card(_object(), objective, [_trace()], query="browser automation MCP server")
    payload = card.model_dump(mode="json", by_alias=True)
    assert payload["schema"] == "AOI_CapabilityTrustCard/v0.1"
    assert payload["route_decision"]["decision"] in {"ALLOW_CANDIDATE", "ALLOW_WITH_LIMITS", "HOLD_POLICY_CLARITY"}
    assert payload["route_decision"]["can_recommend_as_candidate"] is not True or "verified" in payload["route_decision"]["must_not_claim"]
    assert "security certification" in " ".join(payload["not_asserted"]) if "not_asserted" in payload else True
