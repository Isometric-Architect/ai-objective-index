import importlib.util
from pathlib import Path


def test_hf_demo_app_exists_and_run_demo_query_imports():
    app_path = Path("hf_demo/app.py")
    assert app_path.exists()

    spec = importlib.util.spec_from_file_location("hf_demo_app", app_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    summary, rows, payload = module.run_demo_query(
        "cheap image generation API with commercial use terms",
        "low cost commercial use",
        3,
    )
    assert "AI Objective Index" in summary
    assert isinstance(rows, list)
    assert isinstance(payload, dict)
    assert payload["read_only"] is True


def test_hf_demo_requirements_and_readme():
    assert Path("hf_demo/requirements.txt").exists()
    readme = Path("hf_demo/README.md").read_text(encoding="utf-8").lower()
    assert "read-only" in readme
    assert "not a quality guarantee" in readme

