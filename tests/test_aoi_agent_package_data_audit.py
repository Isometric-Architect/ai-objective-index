import zipfile

from ai_objective_index.agent_adoption import package_data_audit
from ai_objective_index.agent_adoption.agent_adoption_packager import package_agent_adoption


def _write_fixture_wheel(path):
    with zipfile.ZipFile(path, "w") as archive:
        for artifact in package_data_audit.SOURCE_ARTIFACTS:
            archive.writestr(f"ai_objective_index-0.3.0a2.data/data/share/ai-objective-index/{artifact.as_posix()}", "{}")


def test_package_data_audit_passes_with_agent_artifacts_in_wheel(monkeypatch, tmp_path):
    package_agent_adoption()
    wheel = tmp_path / "ai_objective_index-0.3.0a2-py3-none-any.whl"
    _write_fixture_wheel(wheel)
    monkeypatch.setattr(package_data_audit, "_wheel_path", lambda: wheel)

    result = package_data_audit.run_package_data_audit(write_result=False)

    assert result["decision"] == "PASS_AGENT_PACKAGE_DATA_READY"
    assert result["agent_discovery_included"] is True
    assert result["schemas_agent_included"] is True
    assert result["examples_included"] is True
    assert result["api_examples_included"] is True


def test_package_data_audit_holds_when_wheel_missing(monkeypatch, tmp_path):
    package_agent_adoption()
    missing = tmp_path / "missing.whl"
    monkeypatch.setattr(package_data_audit, "_wheel_path", lambda: missing)

    result = package_data_audit.run_package_data_audit(write_result=False)

    assert result["decision"] == "HOLD_PACKAGE_DATA_NOT_BUILT"


def test_package_data_audit_detects_secret_like_source(monkeypatch, tmp_path):
    secret_file = tmp_path / "secret.md"
    secret_file.write_text("api_key=" + "sk-" + "exampletoken123456", encoding="utf-8")
    monkeypatch.setattr(package_data_audit, "SOURCE_ARTIFACTS", [secret_file])
    monkeypatch.setattr(package_data_audit, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(package_data_audit, "_wheel_path", lambda: tmp_path / "missing.whl")

    result = package_data_audit.run_package_data_audit(write_result=False)

    assert result["decision"] == "BLOCK_SECRET_FINDING"
