from pathlib import Path

from ai_objective_index.vnext_pypi_resume_gate import run_vnext_pypi_resume_gate


def test_vnext_pypi_resume_gate_writes_instructions():
    result = run_vnext_pypi_resume_gate(write_result=True)
    assert result["pypi_token_required_now"] is False
    assert result["pypi_upload_performed"] is False
    text = Path("public_launch/wave8/NEXT_8Q_A_RESUME_INSTRUCTIONS.md").read_text(encoding="utf-8")
    assert "will not upload to TestPyPI or PyPI" in text
    assert "does not need a PyPI token yet" in text
