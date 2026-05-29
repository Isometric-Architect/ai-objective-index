from pathlib import Path

from ai_objective_index.portfolio.pilot_intake_packager import (
    AGENTSEC_PACKET_PATH,
    DATACAPSULE_PACKET_PATH,
    QIRA_PACKET_PATH,
    RUN_PLAN_PATH,
    package_pilot_intake,
)
from ai_objective_index.real_pypi_upload_gate import _repo_root


def test_packager_creates_three_sample_packets():
    result = package_pilot_intake(sample=True)
    assert len(result["packets"]) == 3
    assert (_repo_root() / AGENTSEC_PACKET_PATH).exists()
    assert (_repo_root() / QIRA_PACKET_PATH).exists()
    assert (_repo_root() / DATACAPSULE_PACKET_PATH).exists()
    assert (_repo_root() / RUN_PLAN_PATH).exists()
    assert result["redaction"]["decision"] == "PASS_REDACTED"


def test_input_packet_does_not_read_local_file_contents(tmp_path):
    path = tmp_path / "sample.diff"
    path.write_text("SECRET_SHOULD_NOT_BE_SCANNED_FROM_FILE_CONTENT", encoding="utf-8")
    result = package_pilot_intake(sample=False, vertical="auto_route", input_path=Path(path))
    assert result["packets"][0]["provided_artifact"]["local_path"].endswith("sample.diff")
    assert "SECRET_SHOULD_NOT_BE_SCANNED_FROM_FILE_CONTENT" not in str(result)
