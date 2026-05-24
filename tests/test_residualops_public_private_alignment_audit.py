from pathlib import Path

from ai_objective_index.residualops_public_private_alignment_audit import (
    run_public_private_alignment_audit,
)


def test_current_public_private_alignment_passes():
    result = run_public_private_alignment_audit(write_result=False)

    assert result["decision"] == "PASS_PUBLIC_PRIVATE_ALIGNMENT"
    assert result["risky_phrase_count"] == 0


def test_public_private_alignment_blocks_overclaim_fixture(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("This is a security certified safe tool.\n", encoding="utf-8")

    result = run_public_private_alignment_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "BLOCK_OVERCLAIM"
    assert result["finding_count"] == 1


def test_public_private_alignment_blocks_private_kernel_fixture(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("private ranking weight: 0.72\n", encoding="utf-8")

    result = run_public_private_alignment_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "BLOCK_PUBLIC_PRIVATE_LEAK"
    assert result["findings"][0]["finding_type"] == "private_kernel"


def test_public_private_alignment_allows_safe_negative_context(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("This is not security certified and cannot authorize actions.\n", encoding="utf-8")

    result = run_public_private_alignment_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "PASS_PUBLIC_PRIVATE_ALIGNMENT"
