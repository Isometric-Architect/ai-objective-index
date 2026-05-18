import importlib.util
from pathlib import Path


def _load_hf_demo_module():
    app_path = Path("hf_demo/app.py")
    spec = importlib.util.spec_from_file_location("hf_demo_app_datascope", app_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_hf_demo_import_safe_and_datascope_aware():
    module = _load_hf_demo_module()

    sample_summary, sample_rows, sample_payload = module.run_demo_query(
        "cheap image generation API",
        data_scope="sample",
    )
    integrated_summary, integrated_rows, integrated_payload = module.run_demo_query(
        "cheap image generation API",
        data_scope="integrated",
    )

    assert "AI Objective Index" in sample_summary
    assert "Data scope: `integrated`" in integrated_summary
    assert isinstance(sample_rows, list)
    assert isinstance(integrated_rows, list)
    assert sample_payload["data_scope"] == "sample"
    assert integrated_payload["data_scope"] == "integrated"
    assert sample_payload["read_only"] is True
