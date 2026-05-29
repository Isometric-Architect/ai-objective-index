from ai_objective_index.portfolio.datacapsule_manifest_summary import SAMPLE_MANIFEST, build_corpus_manifest
from ai_objective_index.portfolio.datacapsule_staleness_risk import summarize_staleness_risk


def test_datacapsule_staleness_unknown_holds():
    result = summarize_staleness_risk(build_corpus_manifest(SAMPLE_MANIFEST))

    assert result["status"] == "HOLD_STALENESS_UNKNOWN"
    assert "declared_update_date" in result["missing_fields"]
