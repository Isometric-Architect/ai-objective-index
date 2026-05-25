from pathlib import Path

from ai_objective_index.datacapsule.package5 import run_datacapsule5_package
from ai_objective_index.datacapsule_claim_audit import run_datacapsule_claim_audit


def test_package_datacapsule5_assets_exist():
    run_datacapsule5_package()
    run_datacapsule_claim_audit(write_result=True)

    expected = [
        "docs/datacapsule5_use_rights_fixture_corpus.md",
        "public_launch/datacapsule5/DATACAPSULE5_FIXTURE_CORPUS.json",
        "public_launch/datacapsule5/DATACAPSULE5_FIXTURE_CORPUS_REPORT.md",
        "public_launch/datacapsule5/DATACAPSULE5_NEGATIVE_CONTROL_RESULT.json",
        "public_launch/datacapsule5/DATACAPSULE5_NEGATIVE_CONTROL_REPORT.md",
        "public_launch/datacapsule5/DATACAPSULE5_PACKAGE_RESULT.json",
        "public_launch/datacapsule5/DATACAPSULE5_NEXT_STEPS.md",
        "public_launch/datacapsule5/DATACAPSULE_CLAIM_BOUNDARY_AUDIT.json",
    ]

    for path in expected:
        assert Path(path).exists()
