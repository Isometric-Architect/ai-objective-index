from ai_objective_index.portfolio.datacapsule_manifest_summary import SAMPLE_MANIFEST, build_corpus_manifest


def test_datacapsule_corpus_manifest_serializes():
    manifest = build_corpus_manifest(SAMPLE_MANIFEST)
    payload = manifest.model_dump(mode="json", by_alias=True)

    assert payload["schema"] == "ResidualOps_DataCapsuleCorpusManifest/v0.1"
    assert payload["local_manifest_only"] is True
    assert payload["raw_content_inspected"] is False
    assert payload["external_network_used"] is False
