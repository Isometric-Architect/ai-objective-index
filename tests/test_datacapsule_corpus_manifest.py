from pathlib import Path

from ai_objective_index.datacapsule.corpus_manifest import (
    SAMPLE_CORPUS_MANIFEST,
    build_corpus_manifest_report,
    build_corpus_manifest_result,
    build_datacapsule2_sample_outputs,
    manifest_to_capsule_metadata,
    read_manifest_path,
    summarize_corpus_manifest,
)


def test_summarize_corpus_manifest_counts_files_and_sources():
    summary = summarize_corpus_manifest(SAMPLE_CORPUS_MANIFEST)

    assert summary.file_count == 3
    assert summary.source_record_count == 3
    assert "MIT" in summary.license_values
    assert summary.risk_flags.stale is True
    assert summary.network_used is False


def test_manifest_to_capsule_metadata_is_local_and_bounded():
    metadata = manifest_to_capsule_metadata(SAMPLE_CORPUS_MANIFEST)

    assert metadata["data_id"] == SAMPLE_CORPUS_MANIFEST["corpus_id"]
    assert metadata["allowed_use"]["retrieve"] is True
    assert metadata["allowed_use"]["act"] is False
    assert "datacapsule2_local_manifest_intake" in metadata["transform_chain"]


def test_build_corpus_manifest_result_preserves_conservative_boundaries():
    result = build_corpus_manifest_result(SAMPLE_CORPUS_MANIFEST, "<memory>")

    assert result.summary.file_count == 3
    assert result.capsule.use_permissions.act.decision == "BLOCK_ACTION_USE"
    assert result.negative_control_false_pass_count == 0
    assert result.local_only is True
    assert result.network_used is False
    assert result.can_certify_quality is False
    assert result.decision == "BLOCK_DATACAPSULE2_USE_RISK"


def test_build_corpus_manifest_report_mentions_no_crawling():
    result = build_corpus_manifest_result(SAMPLE_CORPUS_MANIFEST, "<memory>")
    report = build_corpus_manifest_report(result)

    assert "DataCapsule-2 Corpus Manifest Report" in report
    assert "Crawler used | `False`" in report
    assert "Negative Controls" in report


def test_read_manifest_path(tmp_path):
    path = tmp_path / "corpus_manifest.json"
    path.write_text('{"corpus_id":"fixture.local/path","name":"Path","files":[]}', encoding="utf-8")

    assert read_manifest_path(Path(path))["corpus_id"] == "fixture.local/path"


def test_datacapsule2_sample_writes_outputs():
    result = build_datacapsule2_sample_outputs()

    assert result.negative_control_false_pass_count == 0
    assert Path("public_launch/datacapsule2/DATACAPSULE2_RESULT.json").exists()
    assert Path("public_launch/datacapsule2/DATACAPSULE2_REPORT.md").exists()
