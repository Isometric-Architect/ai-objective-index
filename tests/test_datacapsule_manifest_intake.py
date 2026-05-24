from pathlib import Path

from ai_objective_index.datacapsule.manifest_intake import (
    SAMPLE_CSV_TEXT,
    SAMPLE_JSONL_TEXT,
    build_datacapsule3_sample_outputs,
    build_manifest_intake_report,
    build_manifest_intake_result,
    read_csv_manifest,
    read_jsonl_manifest,
    rows_to_corpus_manifest,
)


def test_read_csv_manifest_normalizes_purpose_and_flags(tmp_path):
    path = tmp_path / "manifest.csv"
    path.write_text(
        "path,source,license,privacy_level,purpose,risk_flags\n"
        "docs/a.md,local,MIT,public_metadata,\"retrieve;summarize\",\"prompt_injection;stale\"\n",
        encoding="utf-8",
    )

    rows = read_csv_manifest(Path(path))

    assert rows[0]["purpose"] == ["retrieve", "summarize"]
    assert rows[0]["risk_flags"]["prompt_injection"] is True
    assert rows[0]["risk_flags"]["stale"] is True


def test_read_jsonl_manifest_normalizes_rows(tmp_path):
    path = tmp_path / "manifest.jsonl"
    path.write_text(SAMPLE_JSONL_TEXT, encoding="utf-8")

    rows = read_jsonl_manifest(Path(path))

    assert len(rows) == 3
    assert rows[1]["purpose"] == ["evaluate"]


def test_rows_to_corpus_manifest_sets_allowed_use():
    rows = [
        {"path": "docs/train.md", "source": "local", "license": "MIT", "privacy_level": "public", "purpose": ["train"]},
        {"path": "docs/eval.md", "source": "local", "license": "MIT", "privacy_level": "public", "purpose": ["evaluate"]},
    ]
    manifest = rows_to_corpus_manifest(rows, "fixture.local/corpus", "Corpus", "csv")

    assert manifest["allowed_use"]["train"] is True
    assert manifest["allowed_use"]["evaluate"] is True
    assert manifest["allowed_use"]["act"] is False


def test_manifest_intake_result_from_csv_passes_local_metadata(tmp_path):
    path = tmp_path / "manifest.csv"
    path.write_text(SAMPLE_CSV_TEXT, encoding="utf-8")

    result = build_manifest_intake_result(path, "fixture.local/csv", "CSV Fixture")

    assert result.source_format == "csv"
    assert result.decision == "BLOCK_DATACAPSULE3_USE_RISK"
    assert result.eval_leak_report.decision == "PASS_EVAL_SEPARATION_LOCAL_METADATA"
    assert result.network_used is False
    assert result.can_prove_eval_cleanliness is False


def test_manifest_intake_blocks_eval_overlap(tmp_path):
    path = tmp_path / "manifest.csv"
    path.write_text(
        "path,source,license,privacy_level,purpose,risk_flags\n"
        "docs/shared.md,local,MIT,public_metadata,\"train;evaluate\",\n",
        encoding="utf-8",
    )

    result = build_manifest_intake_result(path, "fixture.local/overlap", "Overlap")

    assert result.eval_leak_report.decision == "BLOCK_EVAL_LEAK_CONFLICT"
    assert result.eval_leak_report.overlap_paths == ["docs/shared.md"]


def test_manifest_intake_report_mentions_boundaries(tmp_path):
    path = tmp_path / "manifest.csv"
    path.write_text(SAMPLE_CSV_TEXT, encoding="utf-8")
    result = build_manifest_intake_result(path, "fixture.local/report", "Report")
    report = build_manifest_intake_report(result)

    assert "DataCapsule-3 Manifest Intake Report" in report
    assert "Crawler used | `False`" in report
    assert "prove evaluation cleanliness" in report


def test_datacapsule3_sample_writes_outputs():
    result = build_datacapsule3_sample_outputs()

    assert result.source_format == "csv"
    assert Path("public_launch/datacapsule3/DATACAPSULE3_RESULT.json").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_EVAL_LEAK_SEPARATION_REPORT.json").exists()
