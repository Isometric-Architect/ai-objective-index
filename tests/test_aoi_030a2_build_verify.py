from pathlib import Path

from ai_objective_index import aoi_030a2_build_verify as build_verify


def test_build_verify_passes_with_mocked_artifacts(monkeypatch, tmp_path):
    wheel = tmp_path / "dist" / "ai_objective_index-0.3.0a2-py3-none-any.whl"
    sdist = tmp_path / "dist" / "ai_objective_index-0.3.0a2.tar.gz"
    wheel.parent.mkdir()
    wheel.write_text("wheel", encoding="utf-8")
    sdist.write_text("sdist", encoding="utf-8")
    monkeypatch.setattr(build_verify, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(build_verify, "_artifact_contains_marker", lambda path: True)
    monkeypatch.setattr(build_verify, "run_marker_sync", lambda write_result=True: {"decision": "PASS_MARKER_SYNCED_030A2"})

    result = build_verify.run_build_verify(
        runner=lambda command, timeout=600: {"ok": True, "returncode": 0, "stdout": "", "stderr": "", "command": command},
        write_result=False,
    )

    assert result["decision"] == "PASS_BUILD_TWINE_MARKER_SYNCED"
    assert result["wheel_exists"] is True


def test_build_verify_blocks_missing_marker(monkeypatch, tmp_path):
    (tmp_path / "dist").mkdir()
    (tmp_path / build_verify.WHEEL_PATH).write_text("wheel", encoding="utf-8")
    (tmp_path / build_verify.SDIST_PATH).write_text("sdist", encoding="utf-8")
    monkeypatch.setattr(build_verify, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(build_verify, "_artifact_contains_marker", lambda path: False)
    monkeypatch.setattr(build_verify, "run_marker_sync", lambda write_result=True: {"decision": "PASS_MARKER_SYNCED_030A2"})

    result = build_verify.run_build_verify(
        runner=lambda command, timeout=600: {"ok": True, "returncode": 0, "stdout": "", "stderr": "", "command": command},
        write_result=False,
    )

    assert result["decision"] == "HOLD_BUILD_VERIFY_FAILED"
