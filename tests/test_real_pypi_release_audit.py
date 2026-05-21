from ai_objective_index import real_pypi_release_audit


def test_real_pypi_release_audit_upload_and_install_pass(monkeypatch):
    def fake_read(path):
        name = str(path)
        if "UPLOAD" in name:
            return {"result_token": "UPLOAD_SUCCESS", "pypi_project_url": "https://pypi.org/project/ai-objective-index/0.3.0a1/"}
        if "INSTALL" in name:
            return {"decision": "PASS_REAL_PYPI_INSTALL"}
        return {}

    monkeypatch.setattr(real_pypi_release_audit, "_read_json", fake_read)
    monkeypatch.setattr(real_pypi_release_audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(real_pypi_release_audit, "_scan_overclaims", lambda: [])

    result = real_pypi_release_audit.run_real_pypi_release_audit(write_result=False)

    assert result["decision"] == "PASS_REAL_PYPI_RELEASE_VERIFIED"


def test_real_pypi_release_audit_token_finding_blocks(monkeypatch):
    monkeypatch.setattr(real_pypi_release_audit, "_read_json", lambda path: {"result_token": "UPLOAD_SUCCESS", "decision": "PASS_REAL_PYPI_INSTALL"})
    monkeypatch.setattr(real_pypi_release_audit, "tracked_token_findings", lambda: ["token.txt"])
    monkeypatch.setattr(real_pypi_release_audit, "_scan_overclaims", lambda: [])

    result = real_pypi_release_audit.run_real_pypi_release_audit(write_result=False)

    assert result["decision"] == "BLOCK_TOKEN_FINDING"


def test_real_pypi_release_audit_overclaim_blocks(monkeypatch):
    monkeypatch.setattr(real_pypi_release_audit, "_read_json", lambda path: {"result_token": "UPLOAD_SUCCESS", "decision": "PASS_REAL_PYPI_INSTALL"})
    monkeypatch.setattr(real_pypi_release_audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(real_pypi_release_audit, "_scan_overclaims", lambda: [{"path": "README.md", "phrase": "safe tool"}])

    result = real_pypi_release_audit.run_real_pypi_release_audit(write_result=False)

    assert result["decision"] == "BLOCK_OVERCLAIM"
