import json
from pathlib import Path

from ai_objective_index.datacapsule.repository_audit_bundle import (
    ARTIFACT_MANIFEST_PATH,
    BUNDLE_RESULT_PATH,
    CORPUS_AUDIT_REPORT_PATH,
    REVIEW_COMMENT_DRAFT_PATH,
    build_artifact_manifest,
    build_corpus_audit_markdown,
    build_datacapsule6_bundle,
    build_review_comment_draft,
)


def _sample_corpus():
    return {
        "decision": "PASS_DATACAPSULE5_FIXTURE_CORPUS_READY",
        "fixture_count": 2,
        "fixtures": [
            {
                "fixture_id": "safe-retrieval-public-docs",
                "primary_use": "retrieve",
                "risk_theme": "source_traced_retrieval_metadata",
                "expected_decision": "ALLOW_USE",
            },
            {
                "fixture_id": "privacy-risk-training",
                "primary_use": "train",
                "risk_theme": "privacy_risk",
                "expected_decision": "BLOCK_PRIVACY_RISK",
            },
        ],
    }


def _sample_negative_controls():
    return {
        "decision": "PASS_DATACAPSULE5_NEGATIVE_CONTROLS",
        "false_pass_count": 0,
        "mismatch_count": 0,
        "actual_counts": {"allow": 1, "hold": 0, "block": 1},
        "results": [
            {
                "fixture_id": "safe-retrieval-public-docs",
                "expected_decision": "ALLOW_USE",
                "actual_decision": "ALLOW_USE",
                "false_pass": False,
            },
            {
                "fixture_id": "privacy-risk-training",
                "expected_decision": "BLOCK_PRIVACY_RISK",
                "actual_decision": "BLOCK_PRIVACY_RISK",
                "false_pass": False,
            },
        ],
    }


def test_datacapsule6_corpus_audit_markdown_contains_boundaries():
    text = build_corpus_audit_markdown(
        {"decision": "PASS_DATACAPSULE5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS"},
        _sample_corpus(),
        _sample_negative_controls(),
    )

    assert "DataCapsule-6 Repository Corpus Audit Report" in text
    assert "Crawler used | `False`" in text
    assert "External service used | `False`" in text
    assert "Review comment posted | `False`" in text
    assert "BLOCK_PRIVACY_RISK" in text


def test_datacapsule6_review_comment_is_draft_only():
    text = build_review_comment_draft(
        {"decision": "PASS_DATACAPSULE5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS"},
        _sample_corpus(),
        _sample_negative_controls(),
    )

    assert "draft only" in text
    assert "did not post this comment" in text
    assert "crawl directories" in text
    assert "authorize actions" in text


def test_datacapsule6_run_sample_writes_bundle_outputs():
    result = build_datacapsule6_bundle(run_upstream_sample=True)

    assert result.decision == "PASS_DATACAPSULE6_REPOSITORY_AUDIT_BUNDLE"
    assert result.review_comment_posted is False
    assert result.crawler_used is False
    assert result.network_used is False
    assert result.false_pass_count == 0
    assert Path(CORPUS_AUDIT_REPORT_PATH).exists()
    assert Path(REVIEW_COMMENT_DRAFT_PATH).exists()
    assert Path(ARTIFACT_MANIFEST_PATH).exists()
    assert Path(BUNDLE_RESULT_PATH).exists()

    manifest = json.loads(Path(ARTIFACT_MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["decision"] == "PASS_DATACAPSULE6_ARTIFACT_MANIFEST"
    assert manifest["review_comment_posted"] is False
    assert all(item["exists"] for item in manifest["artifacts"])


def test_datacapsule6_manifest_holds_missing_artifact():
    manifest = build_artifact_manifest([Path("public_launch/datacapsule6/NO_SUCH_FILE.md")])

    assert manifest["decision"] == "HOLD_DATACAPSULE6_ARTIFACT_MISSING"
    assert manifest["missing_artifacts"]
