from pathlib import Path

from ai_objective_index.vnext_package_version_audit import run_vnext_package_version_audit


def test_version_audit_default_does_not_modify_files():
    pyproject = Path("pyproject.toml")
    before = pyproject.read_text(encoding="utf-8")
    result = run_vnext_package_version_audit(write_result=True)
    after = pyproject.read_text(encoding="utf-8")
    assert before == after
    assert result["version_change_applied"] is False
    assert result["recommended_version"] == "0.3.0"


def test_version_audit_recommends_or_holds_for_vnext():
    result = run_vnext_package_version_audit(write_result=False)
    assert result["decision"] in {"HOLD_VERSION_DECISION", "PASS_VERSION_APPLIED", "BLOCK_INVALID_VERSION"}
    assert result["pypi_upload_performed"] is False
