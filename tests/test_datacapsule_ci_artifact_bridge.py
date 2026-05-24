from pathlib import Path

from ai_objective_index.datacapsule.ci_artifact_bridge import (
    DataCapsuleCiArtifactBridgeRequest,
    audit_datacapsule4_action_manifest,
    run_ci_artifact_bridge,
    run_sample,
)
from ai_objective_index.datacapsule.manifest_intake import SAMPLE_CSV_TEXT


def test_datacapsule4_run_sample_blocks_action_use_without_external_actions():
    result = run_sample()

    assert result.decision == "BLOCK_DATACAPSULE4_USE_RISK"
    assert result.intake_decision == "BLOCK_DATACAPSULE3_USE_RISK"
    assert result.eval_leak_decision == "PASS_EVAL_SEPARATION_LOCAL_METADATA"
    assert result.directory_crawled is False
    assert result.private_file_contents_read is False
    assert result.github_api_used_by_datacapsule is False
    assert result.token_printed is False


def test_datacapsule4_missing_manifest_holds():
    result = run_ci_artifact_bridge(DataCapsuleCiArtifactBridgeRequest(manifest_path=""))

    assert result.decision == "HOLD_DATACAPSULE4_MANIFEST_REQUIRED"
    assert result.external_actions_performed is False


def test_datacapsule4_clean_manifest_still_blocks_action_authorization(tmp_path):
    manifest_path = tmp_path / "manifest.csv"
    manifest_path.write_text(
        "path,source,license,privacy_level,purpose,risk_flags\n"
        "docs/rag.md,local,MIT,public_metadata,\"retrieve;summarize\",\n",
        encoding="utf-8",
    )

    result = run_ci_artifact_bridge(
        DataCapsuleCiArtifactBridgeRequest(
            manifest_path=str(manifest_path),
            output_dir="public_launch/datacapsule4",
            corpus_id="fixture.local/clean",
            name="Clean Corpus",
        )
    )

    assert result.decision == "BLOCK_DATACAPSULE4_USE_RISK"
    assert result.intake_decision == "BLOCK_DATACAPSULE3_USE_RISK"
    assert result.eval_leak_decision == "PASS_EVAL_SEPARATION_LOCAL_METADATA"


def test_datacapsule4_eval_overlap_blocks(tmp_path):
    manifest_path = tmp_path / "manifest.csv"
    manifest_path.write_text(
        "path,source,license,privacy_level,purpose,risk_flags\n"
        "docs/shared.md,local,MIT,public_metadata,\"train;evaluate\",\n",
        encoding="utf-8",
    )

    result = run_ci_artifact_bridge(
        DataCapsuleCiArtifactBridgeRequest(
            manifest_path=str(manifest_path),
            output_dir="public_launch/datacapsule4",
            corpus_id="fixture.local/overlap",
            name="Overlap Corpus",
        )
    )

    assert result.decision == "BLOCK_DATACAPSULE4_USE_RISK"
    assert result.eval_leak_decision == "BLOCK_EVAL_LEAK_CONFLICT"


def test_datacapsule4_action_manifest_audit_passes_and_no_active_workflow():
    result = audit_datacapsule4_action_manifest()

    assert result["decision"] == "PASS_DATACAPSULE4_ACTION_MANIFEST_SAFE"
    assert result["manifest_exists"] is True
    assert result["example_workflow_exists"] is True
    assert result["active_workflow_created"] is False
    assert not Path(".github/workflows/datacapsule-corpus-manifest-artifact.yml").exists()


def test_datacapsule4_sample_csv_fixture_available():
    assert "docs/rag-guide.md" in SAMPLE_CSV_TEXT
