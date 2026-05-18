from __future__ import annotations

import importlib.util
from pathlib import Path


def test_hf_demo_public_beta_mcp_scope_import_safe() -> None:
    app_path = Path("hf_demo/app.py").resolve()
    spec = importlib.util.spec_from_file_location("hf_demo_app_public_beta_mcp_test", app_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    summary, rows, payload = module.run_demo_query("browser automation MCP", data_scope="public_beta_mcp")

    assert "public_beta_mcp" in summary
    assert payload["read_only"] is True
    assert payload["data_scope"] == "public_beta_mcp"
    assert isinstance(rows, list)
    assert rows or payload["query_result"].get("warnings")
