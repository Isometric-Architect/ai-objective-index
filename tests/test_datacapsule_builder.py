from pathlib import Path

from ai_objective_index.datacapsule.capsule_builder import (
    SAMPLE_DATASET_METADATA,
    build_datacapsule_from_metadata,
    build_datacapsule_report,
    build_datacapsule_result,
    build_datacapsule_sample_outputs,
    read_metadata_path,
)


def test_datacapsule_sample_splits_use_boundaries():
    capsule = build_datacapsule_from_metadata(SAMPLE_DATASET_METADATA)

    assert capsule.use_permissions.retrieve.decision == "ALLOW_USE"
    assert capsule.use_permissions.summarize.decision == "ALLOW_USE"
    assert capsule.use_permissions.train.decision == "HOLD_SOURCE_RIGHTS_REVIEW"
    assert capsule.use_permissions.share.decision == "HOLD_SOURCE_RIGHTS_REVIEW"
    assert capsule.use_permissions.act.decision == "BLOCK_ACTION_USE"
    assert capsule.network_used is False


def test_datacapsule_unknown_license_holds_training():
    capsule = build_datacapsule_from_metadata(
        {
            "data_id": "fixture.local/unknown-rights",
            "name": "Unknown Rights",
            "source": "local",
            "allowed_use": {"train": True, "retrieve": True},
        }
    )

    assert capsule.use_permissions.train.decision == "HOLD_SOURCE_RIGHTS_REVIEW"
    assert capsule.risk_flags.rights_unknown is True


def test_datacapsule_restricted_license_blocks_training_and_share():
    capsule = build_datacapsule_from_metadata(
        {
            "data_id": "fixture.local/restricted",
            "name": "Restricted",
            "source": "local",
            "license": "non-commercial restricted",
            "allowed_use": {"train": True, "share": True, "retrieve": True},
        }
    )

    assert capsule.use_permissions.train.decision == "BLOCK_LICENSE_RESTRICTED"
    assert capsule.use_permissions.share.decision == "BLOCK_LICENSE_RESTRICTED"


def test_datacapsule_privacy_blocks_broad_use():
    capsule = build_datacapsule_from_metadata(
        {
            "data_id": "fixture.local/private",
            "name": "Private",
            "source": "local",
            "license": "internal",
            "allowed_use": {"train": True, "share": True},
            "risk_flags": {"privacy": True},
        }
    )

    assert capsule.use_permissions.train.decision == "BLOCK_PRIVACY_RISK"
    assert capsule.use_permissions.share.decision == "BLOCK_PRIVACY_RISK"


def test_datacapsule_unsupported_claim_blocks():
    capsule = build_datacapsule_from_metadata(
        {
            "data_id": "fixture.local/claim",
            "name": "Claim",
            "source": "local",
            "license": "MIT",
            "description": "This data is privacy compliant and eval clean.",
            "allowed_use": {"retrieve": True},
        }
    )

    assert capsule.use_permissions.retrieve.decision == "BLOCK_UNSUPPORTED_CLAIM"


def test_datacapsule_result_counts_and_report():
    capsule = build_datacapsule_from_metadata(SAMPLE_DATASET_METADATA)
    result = build_datacapsule_result(capsule, "<memory>")
    report = build_datacapsule_report(result)

    assert result.allow_count == 3
    assert result.hold_count == 2
    assert result.block_count == 1
    assert result.decision == "BLOCK_DATACAPSULE1_USE_RISK"
    assert "DataCapsule-1 Report" in report
    assert "Crawler used | `False`" in report


def test_datacapsule_read_metadata_path(tmp_path):
    path = tmp_path / "metadata.json"
    path.write_text('{"data_id":"fixture.local/path","name":"Path","license":"MIT"}', encoding="utf-8")

    assert read_metadata_path(Path(path))["data_id"] == "fixture.local/path"


def test_datacapsule_run_sample_writes_outputs():
    result = build_datacapsule_sample_outputs()

    assert result.decision == "BLOCK_DATACAPSULE1_USE_RISK"
    assert Path("public_launch/datacapsule1/DATACAPSULE1_CAPSULE.json").exists()
    assert Path("public_launch/datacapsule1/DATACAPSULE1_REPORT.md").exists()
    assert Path("public_launch/datacapsule1/DATACAPSULE1_RESULT.json").exists()
