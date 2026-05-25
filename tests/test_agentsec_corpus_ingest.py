import json
from pathlib import Path

from ai_objective_index.agentsec.corpus_ingest import (
    SAMPLE_MANIFEST_CORPUS,
    build_agentsec6_corpus_intake_result,
    load_manifest_corpus,
    write_agentsec6_sample_outputs,
)


def test_agentsec6_sample_corpus_has_expected_mix():
    result = build_agentsec6_corpus_intake_result(SAMPLE_MANIFEST_CORPUS)

    assert result["decision"] == "PASS_AGENTSEC6_LOCAL_CORPUS_INTAKE"
    assert result["manifest_count"] >= 5
    assert result["allow_count"] >= 1
    assert result["hold_count"] >= 1
    assert result["block_count"] >= 1
    assert result["network_used"] is False
    assert result["live_mcp_called"] is False
    assert result["external_tool_executed"] is False
    assert result["can_authorize_action"] is False


def test_agentsec6_directory_loader_reads_json_and_warns_on_unsupported(tmp_path: Path):
    (tmp_path / "safe.json").write_text(json.dumps(SAMPLE_MANIFEST_CORPUS[0]), encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("ignored", encoding="utf-8")

    payloads, warnings, errors = load_manifest_corpus(tmp_path)

    assert len(payloads) == 1
    assert warnings
    assert errors == []


def test_agentsec6_missing_path_returns_error(tmp_path: Path):
    payloads, warnings, errors = load_manifest_corpus(tmp_path / "missing")

    assert payloads == []
    assert warnings == []
    assert errors


def test_agentsec6_writes_sample_outputs():
    result = write_agentsec6_sample_outputs()

    assert result["decision"] == "PASS_AGENTSEC6_LOCAL_CORPUS_INTAKE"
