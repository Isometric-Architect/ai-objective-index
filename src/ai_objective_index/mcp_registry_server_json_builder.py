from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


MCP_DIR = Path(".mcp")
SERVER_JSON_PATH = MCP_DIR / "server.json"
WAVE1_DIR = Path("public_launch") / "wave1"
DRAFT_PATH = WAVE1_DIR / "MCP_REGISTRY_SERVER_JSON_DRAFT.json"
SERVER_NAME = "io.github.Isometric-Architect/ai-objective-index"
VERSION = "0.3.0a2"
SERVER_SCHEMA_URL = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def namespace_is_valid(name: str) -> bool:
    return bool(re.fullmatch(r"io\.github\.[A-Za-z0-9][A-Za-z0-9-]*/[a-z0-9][a-z0-9-]*", name))


def build_server_json() -> dict[str, Any]:
    root = _repo_root()
    entrypoint_exists = (root / "src/ai_objective_index/mcp_stdio_entrypoint.py").exists()
    manifest_exists = (root / "data/generated_mcp_tools_manifest.json").exists()
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8") if (root / "pyproject.toml").exists() else ""
    package_script_exists = "ai-objective-index-mcp" in pyproject
    local_package_artifact_exists = any((root / "dist").glob("*.whl")) if (root / "dist").exists() else False
    release_audit_path = root / "public_launch/wave10_real_pypi/REAL_PYPI_RELEASE_AUDIT_RESULT.json"
    release_audit = {}
    if release_audit_path.exists():
        try:
            loaded = json.loads(release_audit_path.read_text(encoding="utf-8"))
            release_audit = loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            release_audit = {}
    package_artifact_exists = release_audit.get("decision") == "PASS_REAL_PYPI_RELEASE_VERIFIED"
    remote_endpoint_exists = False
    draft_not_submittable = not (package_artifact_exists or remote_endpoint_exists)
    payload: dict[str, Any] = {
        "$schema": SERVER_SCHEMA_URL,
        "name": SERVER_NAME,
        "version": VERSION,
        "description": "Read-only Objective-to-Capability Trust Router for source-traced MCP/API candidates.",
        "repository": {
            "url": "https://github.com/Isometric-Architect/ai-objective-index",
            "source": "github",
        },
        "read_only": True,
        "packages": [
            {
                "registryType": "pypi",
                "identifier": "ai-objective-index",
                "version": VERSION,
                "transport": {"type": "stdio"},
            }
        ],
        "tools_summary": [
            "search",
            "fetch",
            "search_objectives",
            "rank_options",
            "compare_tools",
            "explain_score",
            "get_source_trace",
            "list_missing_fields",
            "generate_decision_receipt",
            "route_objective",
            "get_capability_trust",
            "explain_route_decision",
            "submit_execution_receipt",
            "get_execution_receipt",
            "list_capability_receipts",
            "get_capability_receipt_memory",
            "route_objective_with_receipts",
            "plan_probe_before_use",
            "run_local_probe_plan",
            "get_probe_receipt",
            "get_capability_probe_memory",
            "route_objective_with_probes",
        ],
        "entrypoints": {
            "python_module": "ai_objective_index.mcp_stdio_entrypoint",
            "console_script": "ai-objective-index-mcp" if package_script_exists else None,
            "stdio_entrypoint_exists": entrypoint_exists,
        },
        "artifacts": {
            "manifest_exists": manifest_exists,
            "python_package_artifact_exists": package_artifact_exists,
            "local_python_package_artifact_exists": local_package_artifact_exists,
            "remote_mcp_endpoint_exists": remote_endpoint_exists,
        },
        "limitations": [
            "PyPI package metadata is available for registry submission, but publication remains gated by mcp-publisher, GitHub auth, and explicit confirmation."
            if package_artifact_exists
            else "Draft server metadata only unless a publishable PyPI package or remote MCP endpoint is available.",
            "Registry metadata candidates are not verified, not security certified, and not a quality guarantee.",
            "Probe-before-Use is local metadata and fixture checking, not a live security scanner.",
            "ExecutionReceipt memory is a local evidence sidecar, not independent verification or action authorization.",
            "AOI is read-only and does not perform payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim, or supplier verification.",
        ],
        "vnext_surfaces": {
            "capability_trust": True,
            "objective_router": True,
            "execution_receipt_memory": True,
            "local_probe_before_use": True,
            "external_action_authorization": False,
            "live_mcp_calls": False,
            "external_tool_execution": False,
        },
        "draft_not_submittable": draft_not_submittable,
        "draft_reason": "No package artifact or remote MCP endpoint was found."
        if draft_not_submittable
        else "AOI 0.3.0a2 is the PyPI marker-sync recovery candidate; MCP Registry submission remains gated by mcp-publisher, GitHub auth, PyPI verification, and explicit confirmation.",
        "generated_at": datetime.now(UTC).isoformat(),
    }
    return payload


def write_server_json(write_primary: bool = True) -> dict[str, Any]:
    payload = build_server_json()
    _write_json(DRAFT_PATH, payload)
    if write_primary:
        _write_json(SERVER_JSON_PATH, payload)
    return payload


def main() -> None:
    payload = write_server_json()
    print(
        "mcp_registry_server_json_builder: "
        f"name={payload['name']} "
        f"draft_not_submittable={payload['draft_not_submittable']}"
    )


if __name__ == "__main__":
    main()
