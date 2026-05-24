from pathlib import Path


def test_datacapsule1_docs_exist():
    for path in [
        "docs/datacapsule_engine_plan.md",
        "docs/datacapsule1_local_capsule.md",
        "docs/datacapsule_use_rights.md",
        "docs/datacapsule_limitations.md",
    ]:
        assert Path(path).exists(), path


def test_datacapsule1_outputs_exist_after_sample():
    from ai_objective_index.datacapsule.capsule_builder import build_datacapsule_sample_outputs
    from ai_objective_index.datacapsule_claim_audit import run_datacapsule_claim_audit

    build_datacapsule_sample_outputs()
    run_datacapsule_claim_audit()

    for path in [
        "public_launch/datacapsule1/DATACAPSULE1_SAMPLE_METADATA.json",
        "public_launch/datacapsule1/DATACAPSULE1_CAPSULE.json",
        "public_launch/datacapsule1/DATACAPSULE1_REPORT.md",
        "public_launch/datacapsule1/DATACAPSULE1_RESULT.json",
        "public_launch/datacapsule1/DATACAPSULE1_NEXT_STEPS.md",
        "public_launch/datacapsule1/DATACAPSULE_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path
