from ai_objective_index.portfolio.datacapsule_manifest_summary import SAMPLE_MANIFEST, build_corpus_manifest
from ai_objective_index.portfolio.datacapsule_privacy_risk import build_privacy_risk_summary


def test_datacapsule_privacy_unknown_creates_hold():
    summary = build_privacy_risk_summary(build_corpus_manifest(SAMPLE_MANIFEST))

    assert summary.privacy_status == "HOLD_PII_UNKNOWN"
    assert "declared_pii_status" in summary.missing_fields


def test_datacapsule_declared_sensitive_data_blocks():
    payload = dict(SAMPLE_MANIFEST)
    payload["declared_pii_status"] = "present"
    summary = build_privacy_risk_summary(build_corpus_manifest(payload))

    assert summary.privacy_status == "BLOCK_DECLARED_SENSITIVE_DATA"
