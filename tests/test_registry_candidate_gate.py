from __future__ import annotations

from datetime import UTC, datetime

from ai_objective_index.models import ActionObject, SourceTrace
from ai_objective_index.registry_intake.registry_candidate_gate import (
    BLOCK_FORBIDDEN_STATUS,
    BLOCK_INVALID_URL,
    BLOCK_NO_TRACE,
    HOLD_FIXTURE_ONLY,
    HOLD_MISSING_REPOSITORY,
    PASS_PUBLIC_BETA_CANDIDATE,
    evaluate_registry_beta_candidate,
)


def _object(**overrides):
    payload = {
        "object_id": "mcp-registry-example-0-1-0",
        "name": "io.github.example/real-candidate",
        "object_type": "MCPServer",
        "summary": "Registry metadata for a browser automation MCP server.",
        "official_url": "https://registry.modelcontextprotocol.io/v0.1/servers/io.github.example/real-candidate/versions/0.1.0",
        "source_urls": ["https://registry.modelcontextprotocol.io/v0.1/servers/io.github.example/real-candidate/versions/0.1.0"],
        "capabilities": ["mcp_server", "browser_automation"],
        "categories": ["mcp_server", "mcp_registry"],
        "pricing": {},
        "policies": {"registry_source": "official_mcp_registry_metadata"},
        "docs": {
            "repository_url": "https://github.com/example/real-candidate",
            "registry_url": "https://registry.modelcontextprotocol.io/v0.1/servers/io.github.example/real-candidate/versions/0.1.0",
        },
        "status": "EXTRACTED_UNVERIFIED",
        "confidence": 0.65,
        "missing_fields": [],
        "package_metadata": [{"registry": "npm", "name": "@example/real-candidate"}],
    }
    payload.update(overrides)
    return ActionObject.model_validate(payload)


def _trace(object_id="mcp-registry-example-0-1-0"):
    return SourceTrace.model_validate(
        {
            "trace_id": f"trace-{object_id}-name",
            "object_id": object_id,
            "field": "name",
            "source_url": "https://registry.modelcontextprotocol.io/v0.1/servers/io.github.example/real-candidate/versions/0.1.0",
            "source_title": "Official MCP Registry record",
            "source_snippet": "io.github.example/real-candidate",
            "retrieved_at": datetime.now(UTC).isoformat(),
            "confidence": 0.7,
            "source_rank": "A",
        }
    )


def test_live_or_manual_raw_object_with_trace_passes_public_beta_candidate() -> None:
    result = evaluate_registry_beta_candidate(_object(), [_trace()])

    assert result["decision"] == PASS_PUBLIC_BETA_CANDIDATE
    assert result["beta_candidate"] is True
    assert result["verified"] is False
    assert result["action_ready"] is False


def test_fixture_object_holds_or_blocks() -> None:
    result = evaluate_registry_beta_candidate(_object(fixture_only=True), [_trace()], source_mode="fixture")

    assert result["decision"] == HOLD_FIXTURE_ONLY
    assert result["beta_candidate"] is False


def test_verified_or_action_ready_is_blocked() -> None:
    result = evaluate_registry_beta_candidate(_object(status="VERIFIED"), [_trace()])

    assert BLOCK_FORBIDDEN_STATUS in result["blocks"]
    assert result["beta_candidate"] is False


def test_no_trace_is_blocked() -> None:
    result = evaluate_registry_beta_candidate(_object(), [])

    assert BLOCK_NO_TRACE in result["blocks"]
    assert result["beta_candidate"] is False


def test_invalid_url_is_blocked() -> None:
    result = evaluate_registry_beta_candidate(_object(official_url="not-a-url"), [_trace()])

    assert BLOCK_INVALID_URL in result["blocks"]
    assert result["beta_candidate"] is False


def test_missing_repo_can_still_be_candidate_with_description_and_package() -> None:
    action_object = _object(docs={"registry_url": "https://registry.modelcontextprotocol.io/v0.1/servers/x/versions/0.1.0"})
    result = evaluate_registry_beta_candidate(action_object, [_trace()])

    assert HOLD_MISSING_REPOSITORY in result["holds"]
    assert result["beta_candidate"] is True
