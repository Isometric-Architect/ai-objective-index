from ai_objective_index.portfolio.datacapsule_eval_leakage import build_eval_leakage_summary
from ai_objective_index.portfolio.datacapsule_manifest_summary import SAMPLE_MANIFEST, build_corpus_manifest


def test_datacapsule_eval_overlap_unknown_creates_hold():
    summary = build_eval_leakage_summary(build_corpus_manifest(SAMPLE_MANIFEST))

    assert summary.leakage_status == "HOLD_EVAL_OVERLAP_UNKNOWN"
    assert "declared_eval_overlap_status" in summary.missing_fields


def test_datacapsule_declared_eval_overlap_blocks():
    payload = dict(SAMPLE_MANIFEST)
    payload["declared_eval_overlap_status"] = "present"
    summary = build_eval_leakage_summary(build_corpus_manifest(payload))

    assert summary.leakage_status == "BLOCK_DECLARED_EVAL_CONTAMINATION"
