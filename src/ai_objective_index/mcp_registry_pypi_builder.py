from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .package_metadata_audit import MCP_NAME, RECOMMENDED_VERSION


WAVE2_DIR = Path("public_launch") / "wave2"
RESULT_PATH = WAVE2_DIR / "MCP_REGISTRY_PYPI_SERVER_JSON_RESULT.json"
SERVER_JSON_PATH = Path(".mcp") / "server.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def build_pypi_server_json(pypi_uploaded: bool = False) -> dict[str, Any]:
    status = "READY_FOR_SUBMISSION" if pypi_uploaded else "READY_BUT_PYPI_UPLOAD_REQUIRED"
    return {
        "name": MCP_NAME,
        "title": "AI Objective Index",
        "version": RECOMMENDED_VERSION,
        "description": "Read-only MCP/API benchmark engine for objective-based ranking and comparison of AI tools, APIs, SaaS products, and MCP servers with source traces.",
        "repository": {
            "url": "https://github.com/Isometric-Architect/ai-objective-index",
            "source": "github",
        },
        "packages": [
            {
                "registryType": "pypi",
                "identifier": "ai-objective-index",
                "version": RECOMMENDED_VERSION,
                "transport": {"type": "stdio"},
            }
        ],
        "tools": [
            "search",
            "fetch",
            "search_objectives",
            "rank_options",
            "compare_tools",
            "explain_score",
            "get_source_trace",
            "list_missing_fields",
            "generate_decision_receipt",
        ],
        "read_only": True,
        "limitations": [
            "not verified",
            "not security certified",
            "not a quality guarantee",
            "no purchasing advice",
            "no payment, booking, login, email, purchase, or contract actions",
            "read-only local/package-based MCP stdio server",
        ],
        "server_json_status": status,
        "pypi_upload_required": not pypi_uploaded,
        "mcp_registry_submission_performed": False,
        "generated_at": datetime.now(UTC).isoformat(),
    }


def write_pypi_server_json(pypi_uploaded: bool = False) -> dict[str, Any]:
    payload = build_pypi_server_json(pypi_uploaded=pypi_uploaded)
    _write_json(SERVER_JSON_PATH, payload)
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "server_json_path": str(SERVER_JSON_PATH),
        "server_json_status": payload["server_json_status"],
        "name": payload["name"],
        "registry_type": payload["packages"][0]["registryType"],
        "identifier": payload["packages"][0]["identifier"],
        "version": payload["version"],
        "pypi_upload_required": payload["pypi_upload_required"],
        "token_printed": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
    }
    _write_json(RESULT_PATH, result)
    return result


def main() -> None:
    result = write_pypi_server_json()
    print(
        "mcp_registry_pypi_builder: "
        f"{result['server_json_status']} "
        f"name={result['name']} "
        f"registryType={result['registry_type']}"
    )


if __name__ == "__main__":
    main()
