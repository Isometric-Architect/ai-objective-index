from pathlib import Path

from ai_objective_index.datacapsule.repository_audit_bundle import build_datacapsule6_bundle
from ai_objective_index.datacapsule_claim_audit import run_datacapsule_claim_audit


ROOT = Path(__file__).resolve().parents[1]


def test_datacapsule6_docs_exist():
    for relative in [
        "docs/datacapsule6_repository_corpus_audit_bundle.md",
        "docs/datacapsule_repository_audit_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_datacapsule6_outputs_exist_after_generation():
    build_datacapsule6_bundle(run_upstream_sample=True)
    run_datacapsule_claim_audit(write_result=True)

    for relative in [
        "public_launch/datacapsule6/DATACAPSULE6_CORPUS_AUDIT_REPORT.md",
        "public_launch/datacapsule6/DATACAPSULE6_REVIEW_COMMENT_DRAFT.md",
        "public_launch/datacapsule6/DATACAPSULE6_ARTIFACT_MANIFEST.json",
        "public_launch/datacapsule6/DATACAPSULE6_BUNDLE_RESULT.json",
        "public_launch/datacapsule6/DATACAPSULE6_NEXT_STEPS.md",
        "public_launch/datacapsule6/DATACAPSULE_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert (ROOT / relative).exists(), relative


def test_datacapsule6_report_does_not_post_comment():
    build_datacapsule6_bundle(run_upstream_sample=True)
    text = (ROOT / "public_launch/datacapsule6/DATACAPSULE6_REVIEW_COMMENT_DRAFT.md").read_text(encoding="utf-8")
    report = (ROOT / "public_launch/datacapsule6/DATACAPSULE6_CORPUS_AUDIT_REPORT.md").read_text(encoding="utf-8")

    assert "draft only" in text
    assert "Review comment posted | `False`" in report
    assert "crawl directories" in text
