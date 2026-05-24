from pathlib import Path


def test_datacapsule3_docs_exist():
    assert Path("docs/datacapsule3_manifest_intake.md").exists()
    assert Path("docs/datacapsule_eval_leak_separation.md").exists()


def test_datacapsule3_public_outputs_exist():
    assert Path("public_launch/datacapsule3/DATACAPSULE3_SAMPLE_MANIFEST.csv").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_SAMPLE_MANIFEST.jsonl").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_NORMALIZED_MANIFEST.json").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_CORPUS_CAPSULE.json").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_CORPUS_RESULT.json").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_EVAL_LEAK_SEPARATION_REPORT.json").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_RESULT.json").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_REPORT.md").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_NEXT_STEPS.md").exists()
    assert Path("public_launch/datacapsule3/DATACAPSULE3_CLAIM_BOUNDARY_AUDIT.json").exists()
