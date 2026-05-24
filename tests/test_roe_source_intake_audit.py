from pathlib import Path
from zipfile import ZipFile

from ai_objective_index.roe_source_intake_audit import QBCPL_ZIP, run_source_intake_audit


def _write_zip(path: Path) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr("QBCPL_RUN019_README.md", "claim ceiling: internal source only")


def test_source_intake_audit_records_zip_without_allowing_commit(tmp_path):
    _write_zip(tmp_path / QBCPL_ZIP)

    result = run_source_intake_audit(write_result=False, root=tmp_path, git_files=[])

    assert result["decision"] == "PASS_SOURCE_INPUTS_PROTECTED"
    assert result["qbcpl_zip"]["exists"] is True
    assert result["source_inputs_commit_allowed"] is False
    assert result["external_actions_performed"] is False


def test_source_intake_audit_blocks_tracked_internal_source(tmp_path):
    _write_zip(tmp_path / QBCPL_ZIP)

    result = run_source_intake_audit(write_result=False, root=tmp_path, git_files=[QBCPL_ZIP])

    assert result["decision"] == "BLOCK_INTERNAL_SOURCE_TRACKED"
    assert QBCPL_ZIP in result["tracked_internal_source_findings"]


def test_source_intake_audit_missing_sources_holds(tmp_path):
    result = run_source_intake_audit(write_result=False, root=tmp_path, git_files=[])

    assert result["decision"] == "HOLD_SOURCE_INPUTS_MISSING"
