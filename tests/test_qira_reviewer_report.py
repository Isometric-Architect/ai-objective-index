import json
from pathlib import Path

from ai_objective_index.qira.reviewer_report import (
    ARTIFACT_MANIFEST_PATH,
    BUNDLE_RESULT_PATH,
    PR_COMMENT_DRAFT_PATH,
    REVIEWER_REPORT_PATH,
    build_artifact_manifest,
    build_pr_comment_draft,
    build_qira8_bundle,
    build_reviewer_markdown,
)


def test_qira8_build_reviewer_markdown_contains_boundaries():
    review = {
        "decision": "PASS_QIRA6_REVIEW",
        "release_gate_review": {
            "release_gate_decision": "PASS_CONTRACT_SCOPED",
            "action_license": {
                "patch_draft": "ALLOW",
                "pr_open": "ALLOW",
                "merge": "HOLD",
                "deploy": "BLOCK",
                "public_claim": "ALLOW_SCOPED_INTERNAL",
                "decision_reason": "Scoped evidence only.",
                "must_not_claim": ["do not claim security certification"],
            },
            "path_summary": {"changed_file_count": 2, "category_counts": {"source": 1, "test": 1}},
            "test_command_contract_decision": "PASS_TEST_COMMAND_CONTRACT",
            "test_command_summary": {"command_count": 1},
        },
        "commands_executed_by_qira": False,
        "github_api_used_by_qira": False,
    }
    bridge = {"decision": "PASS_QIRA7_CI_EVIDENCE_BRIDGE"}
    validation = {"decision": "PASS_CI_EVIDENCE_ACCEPTED", "tests_passed": True}

    text = build_reviewer_markdown(review, bridge, validation)

    assert "QIRA Reviewer Report" in text
    assert "Merge | `HOLD`" in text
    assert "Deploy | `BLOCK`" in text
    assert "GitHub API used by QIRA | `False`" in text


def test_qira8_pr_comment_is_draft_only():
    text = build_pr_comment_draft(
        {"decision": "PASS_QIRA6_REVIEW", "release_gate_review": {"release_gate_decision": "PASS_CONTRACT_SCOPED", "action_license": {}}},
        {"validation_decision": "PASS_CI_EVIDENCE_ACCEPTED"},
        {},
    )

    assert "draft only" in text
    assert "QIRA did not execute project commands" in text


def test_qira8_run_sample_writes_bundle_outputs():
    result = build_qira8_bundle(run_upstream_sample=True)

    assert result.decision == "PASS_QIRA8_REVIEWER_BUNDLE"
    assert result.pr_comment_posted is False
    assert Path(REVIEWER_REPORT_PATH).exists()
    assert Path(PR_COMMENT_DRAFT_PATH).exists()
    assert Path(ARTIFACT_MANIFEST_PATH).exists()
    assert Path(BUNDLE_RESULT_PATH).exists()

    manifest = json.loads(Path(ARTIFACT_MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["decision"] == "PASS_QIRA8_ARTIFACT_MANIFEST"
    assert manifest["pr_comment_posted"] is False
    assert all(item["exists"] for item in manifest["artifacts"])


def test_qira8_manifest_holds_missing_artifact():
    manifest = build_artifact_manifest([Path("public_launch/qira8/NO_SUCH_FILE.md")])

    assert manifest["decision"] == "HOLD_QIRA8_ARTIFACT_MISSING"
    assert manifest["missing_artifacts"]
