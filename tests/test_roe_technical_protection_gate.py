from pathlib import Path
from zipfile import ZipFile

from ai_objective_index.roe_source_intake_audit import QBCPL_ZIP
from ai_objective_index.roe_technical_protection_gate import (
    REQUIRED_GITIGNORE_PATTERNS,
    missing_gitignore_patterns,
    run_protection_gate,
)


def _write_minimal_root(root: Path) -> None:
    with ZipFile(root / QBCPL_ZIP, "w") as archive:
        archive.writestr("QBCPL_RUN019_README.md", "internal source")
    (root / ".gitignore").write_text("\n".join(REQUIRED_GITIGNORE_PATTERNS) + "\n", encoding="utf-8")


def test_protection_gate_passes_with_ignored_untracked_source_inputs(tmp_path):
    _write_minimal_root(tmp_path)

    result = run_protection_gate(write_result=False, root=tmp_path, git_files=[])

    assert result["decision"] == "PASS_READY_FOR_QIRA_MVP"
    assert result["selected_next_package"] == "QIRA-1"
    assert result["mcp_registry_submission_performed"] is False


def test_protection_gate_holds_when_gitignore_missing(tmp_path):
    with ZipFile(tmp_path / QBCPL_ZIP, "w") as archive:
        archive.writestr("QBCPL_RUN019_README.md", "internal source")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")

    result = run_protection_gate(write_result=False, root=tmp_path, git_files=[])

    assert result["decision"] == "HOLD_GITIGNORE_HARDENING_REQUIRED"
    assert missing_gitignore_patterns(tmp_path)


def test_protection_gate_blocks_tracked_internal_source(tmp_path):
    _write_minimal_root(tmp_path)

    result = run_protection_gate(write_result=False, root=tmp_path, git_files=[QBCPL_ZIP])

    assert result["decision"] == "BLOCK_INTERNAL_SOURCE_EXPOSURE"
