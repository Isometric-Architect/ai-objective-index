from pathlib import Path


def test_datacapsule2_docs_exist():
    assert Path("docs/datacapsule2_corpus_manifest.md").exists()
    assert Path("docs/datacapsule_negative_controls.md").exists()


def test_datacapsule2_public_outputs_exist():
    assert Path("public_launch/datacapsule2/DATACAPSULE2_SAMPLE_CORPUS_MANIFEST.json").exists()
    assert Path("public_launch/datacapsule2/DATACAPSULE2_CORPUS_CAPSULE.json").exists()
    assert Path("public_launch/datacapsule2/DATACAPSULE2_RESULT.json").exists()
    assert Path("public_launch/datacapsule2/DATACAPSULE2_REPORT.md").exists()
    assert Path("public_launch/datacapsule2/DATACAPSULE2_NEGATIVE_CONTROL_RESULT.json").exists()
    assert Path("public_launch/datacapsule2/DATACAPSULE2_NEXT_STEPS.md").exists()
