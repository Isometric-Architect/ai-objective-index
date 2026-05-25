from pathlib import Path

from ai_objective_index.residualops_artifact_manifest import (
    build_shared_artifact_manifest,
    run_shared_artifact_manifest,
)


def test_shared_artifact_manifest_builds_current_verticals():
    result = build_shared_artifact_manifest()

    assert result["decision"] == "PASS_ROE2_SHARED_MANIFEST_READY"
    assert result["vertical_count"] == 3
    assert result["missing_artifacts"] == []
    assert result["external_actions_performed"] is False


def test_shared_artifact_manifest_detects_missing_artifact(tmp_path: Path):
    result = build_shared_artifact_manifest(root=tmp_path)

    assert result["decision"] == "HOLD_ROE2_MISSING_ARTIFACTS"
    assert result["missing_artifacts"]


def test_shared_artifact_manifest_writes_output():
    result = run_shared_artifact_manifest(write_result=True)

    assert result["decision"] == "PASS_ROE2_SHARED_MANIFEST_READY"
