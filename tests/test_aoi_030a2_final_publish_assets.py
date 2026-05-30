from pathlib import Path


def test_final_publish_docs_exist():
    for path in [
        "docs/aoi_030a2_final_publish.md",
        "docs/aoi_pypi_upload_final.md",
        "docs/aoi_mcp_registry_final_publish.md",
        "docs/aoi_agent_native_distribution.md",
    ]:
        assert Path(path).exists(), path


def test_final_publish_modules_exist():
    for path in [
        "src/ai_objective_index/aoi_030a2_final_preflight.py",
        "src/ai_objective_index/aoi_030a2_final_pypi_upload_gate.py",
        "src/ai_objective_index/aoi_030a2_final_pypi_upload_runner.py",
        "src/ai_objective_index/aoi_030a2_final_pypi_verify.py",
        "src/ai_objective_index/aoi_030a2_final_mcp_registry_gate.py",
        "src/ai_objective_index/aoi_030a2_final_mcp_registry_publish.py",
        "src/ai_objective_index/aoi_030a2_final_mcp_registry_reconcile.py",
        "src/ai_objective_index/aoi_030a2_final_publish_report.py",
    ]:
        assert Path(path).exists(), path


def test_final_publish_report_boundaries(monkeypatch):
    from ai_objective_index import aoi_030a2_final_publish_report as report_module

    monkeypatch.setattr(report_module, "_ensure_outputs", lambda: None)
    monkeypatch.setattr(report_module, "_decision", lambda path: "PASS")
    report = report_module.build_final_report()

    assert "Agent-native capability card" in report
    assert "No security certification" in report
    assert "No product-readiness claim" in report
    assert "No action authorization" in report
