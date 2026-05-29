from ai_objective_index.portfolio.datacapsule_manifest_summary import SAMPLE_MANIFEST, build_corpus_manifest
from ai_objective_index.portfolio.datacapsule_source_rights import build_source_rights_summary


def test_datacapsule_source_rights_unknown_creates_hold():
    summary = build_source_rights_summary(build_corpus_manifest(SAMPLE_MANIFEST))

    assert summary.rights_status == "HOLD_LICENSE_MISSING"
    assert "declared_license" in summary.missing_fields


def test_datacapsule_declared_disallowed_use_blocks():
    payload = dict(SAMPLE_MANIFEST)
    payload["declared_license"] = "MIT"
    payload["declared_terms"] = "repository-local terms"
    payload["declared_collection_method"] = "owner-provided"
    payload["declared_disallowed_uses"] = ["train"]
    summary = build_source_rights_summary(build_corpus_manifest(payload))

    assert summary.rights_status == "BLOCK_DISALLOWED_USE_DECLARED"
