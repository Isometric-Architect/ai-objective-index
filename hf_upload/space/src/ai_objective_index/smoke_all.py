from __future__ import annotations

import importlib
import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import mcp_tools
from .mcp_compat import fetch, search
from .seed_loader import load_sample_index


DEFAULT_OUTPUT_PATH = Path("data/generated/smoke_all_result_v0_1.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _check(name: str, func) -> dict[str, Any]:
    try:
        details = func()
        return {"name": name, "pass": True, "details": details}
    except Exception as exc:
        return {"name": name, "pass": False, "error": str(exc)}


def _hf_demo_import_safe() -> dict[str, Any]:
    path = _repo_root() / "hf_demo" / "app.py"
    spec = importlib.util.spec_from_file_location("hf_demo_app_smoke_all", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load hf_demo/app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary, rows, payload = module.run_demo_query("api", data_scope="sample")
    return {"summary_contains_aoi": "AI Objective Index" in summary, "rows": len(rows), "read_only": payload["read_only"]}


def _api_probe() -> dict[str, Any]:
    from fastapi.testclient import TestClient

    from .api import app

    client = TestClient(app)
    status = client.get("/status")
    search_response = client.get("/search", params={"query": "api", "limit": 3})
    return {"status_code": status.status_code, "search_code": search_response.status_code}


def run_smoke_all(write_result: bool = True) -> dict[str, Any]:
    checks = [
        _check("import_ai_objective_index", lambda: {"module": importlib.import_module("ai_objective_index").__name__}),
        _check("load_sample_index", lambda: {"count": len(load_sample_index())}),
        _check("mcp_compat_search", lambda: {"count": len(search("api", limit=3)["results"])}),
        _check(
            "mcp_compat_fetch",
            lambda: {"status": fetch(search("api", limit=1)["results"][0]["object_id"])["status"]},
        ),
        _check("mcp_tools_search_objectives", lambda: {"count": len(mcp_tools.search_objectives("api", limit=3)["results"])}),
        _check("api_status_search", _api_probe),
        _check("manifest_exists", lambda: {"exists": (_repo_root() / "data/generated_mcp_tools_manifest.json").exists()}),
        _check("openapi_exists", lambda: {"exists": (_repo_root() / "api/openapi.json").exists()}),
        _check("hf_demo_import_safe", _hf_demo_import_safe),
        _check(
            "release_docs_if_generated",
            lambda: {
                "release_dir_exists": (_repo_root() / "release/public_beta_v0_1").exists(),
                "readme_exists": (_repo_root() / "release/public_beta_v0_1/README_PUBLIC_BETA.md").exists(),
            },
        ),
    ]
    errors = [check for check in checks if not check["pass"]]
    manifest = json.loads((_repo_root() / "data/generated_mcp_tools_manifest.json").read_text(encoding="utf-8"))
    tool_names = {tool["name"] for tool in manifest.get("tools", [])}
    forbidden_actions_exposed = bool(tool_names & set(mcp_tools.FORBIDDEN_ACTIONS))
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "pass": not errors and not forbidden_actions_exposed,
        "checks": checks,
        "errors": errors,
        "live_network_used": False,
        "forbidden_actions_exposed": forbidden_actions_exposed,
        "read_only": True,
        "actual_publish_performed": False,
    }
    if write_result:
        path = _repo_root() / DEFAULT_OUTPUT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result["output_path"] = str(path)
    return result


def main() -> None:
    result = run_smoke_all()
    print(
        "smoke_all: "
        f"pass={result['pass']} "
        f"checks={len(result['checks'])} "
        f"errors={len(result['errors'])} "
        f"forbidden_actions_exposed={result['forbidden_actions_exposed']}"
    )
    if result.get("output_path"):
        print(f"Saved smoke_all result: {result['output_path']}")


if __name__ == "__main__":
    main()
