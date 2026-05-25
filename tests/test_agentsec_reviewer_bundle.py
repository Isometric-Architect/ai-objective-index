import json
from pathlib import Path

from ai_objective_index.agentsec.reviewer_bundle import (
    ARTIFACT_MANIFEST_PATH,
    BUNDLE_RESULT_PATH,
    PR_COMMENT_DRAFT_PATH,
    REVIEWER_REPORT_PATH,
    build_agentsec7_bundle,
    build_artifact_manifest,
    build_pr_comment_draft,
    build_reviewer_markdown,
)


def _sample_policy_gate():
    return {
        "decision": "PASS_AGENTSEC_POLICY_GATE",
        "packets": [
            {
                "tool_id": "fixture.local/browser-research-helper",
                "risk_decision": "HOLD_REVIEW_REQUIRED",
                "integration_type": "mcp_server",
                "provider": "local-fixture",
                "policy_hold_reasons": ["network or browser access requires review"],
                "policy_block_reasons": [],
            },
            {
                "tool_id": "fixture.local/checkout-helper",
                "risk_decision": "BLOCK_POLICY_RISK",
                "integration_type": "agent_tool",
                "provider": "local-fixture",
                "policy_hold_reasons": [],
                "policy_block_reasons": ["forbidden action language"],
            },
        ],
    }


def test_agentsec7_build_reviewer_markdown_contains_boundaries():
    package = {"decision": "PASS_AGENTSEC6_LOCAL_MANIFEST_CORPUS_PACKAGE", "manifest_count": 2, "allow_count": 0, "hold_count": 1, "block_count": 1}
    intake = {"decision": "PASS_AGENTSEC6_LOCAL_CORPUS_INTAKE", "manifest_count": 2, "allow_count": 0, "hold_count": 1, "block_count": 1}

    text = build_reviewer_markdown(package, intake, _sample_policy_gate())

    assert "AgentSec-7 Reviewer Report" in text
    assert "GitHub API used | `False`" in text
    assert "Live MCP calls | `False`" in text
    assert "External tool execution | `False`" in text
    assert "BLOCK_POLICY_RISK" in text


def test_agentsec7_pr_comment_is_draft_only():
    text = build_pr_comment_draft(
        {"decision": "PASS_AGENTSEC6_LOCAL_MANIFEST_CORPUS_PACKAGE", "manifest_count": 2},
        {"decision": "PASS_AGENTSEC6_LOCAL_CORPUS_INTAKE", "manifest_count": 2},
        _sample_policy_gate(),
    )

    assert "draft only" in text
    assert "did not post this comment" in text
    assert "call live MCP servers" in text
    assert "authorize external actions" in text


def test_agentsec7_run_sample_writes_bundle_outputs():
    result = build_agentsec7_bundle(run_upstream_sample=True)

    assert result.decision == "PASS_AGENTSEC7_REVIEWER_BUNDLE"
    assert result.pr_comment_posted is False
    assert result.github_api_used is False
    assert result.live_mcp_called is False
    assert Path(REVIEWER_REPORT_PATH).exists()
    assert Path(PR_COMMENT_DRAFT_PATH).exists()
    assert Path(ARTIFACT_MANIFEST_PATH).exists()
    assert Path(BUNDLE_RESULT_PATH).exists()

    manifest = json.loads(Path(ARTIFACT_MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["decision"] == "PASS_AGENTSEC7_ARTIFACT_MANIFEST"
    assert manifest["pr_comment_posted"] is False
    assert all(item["exists"] for item in manifest["artifacts"])


def test_agentsec7_manifest_holds_missing_artifact():
    manifest = build_artifact_manifest([Path("public_launch/agentsec7/NO_SUCH_FILE.md")])

    assert manifest["decision"] == "HOLD_AGENTSEC7_ARTIFACT_MISSING"
    assert manifest["missing_artifacts"]
