from pathlib import Path

from ai_objective_index.portfolio.datacapsule_pilot_packager import RECEIPT_PATH, package_datacapsule_pilot


def test_datacapsule_pilot_packager_creates_artifacts():
    result = package_datacapsule_pilot(sample=True)

    assert result["redaction"]["decision"] == "PASS_REDACTED"
    assert result["receipt"]["decision_summary"]["block_count"] == 1
    for path in result["paths"].values():
        assert Path(path).exists(), path


def test_datacapsule_pilot_packager_does_not_use_network_or_training():
    result = package_datacapsule_pilot(sample=True)

    assert Path(RECEIPT_PATH).exists()
    assert result["raw_content_inspected"] is False
    assert result["external_network_used"] is False
    assert result["data_uploaded"] is False
    assert result["model_trained"] is False
