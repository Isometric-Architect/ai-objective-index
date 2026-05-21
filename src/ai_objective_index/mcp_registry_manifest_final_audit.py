from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .package_metadata_audit import MCP_MARKER, MCP_NAME
from .real_pypi_release_audit import OUTPUT_PATH as PYPI_RELEASE_AUDIT_PATH
from .real_pypi_upload_gate import PACKAGE_NAME, TARGET_VERSION, _repo_root, tracked_token_findings


OUTPUT_PATH = Path("public_launch") / "wave11_mcp_registry" / "MCP_REGISTRY_MANIFEST_FINAL_AUDIT.json"
GITHUB_REPO_URL = "https://github.com/Isometric-Architect/ai-objective-index"
PYPI_PROJECT_URL = "https://pypi.org/project/ai-objective-index/0.3.0a1/"
RISKY_PHRASES = [
    "verified capability",
    "safe tool",
    "security certified",
    "quality guaranteed",
    "product ready",
    "product-ready",
    "production ready",
    "production-ready",
    "action authorization",
]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_text(path: str) -> str:
    full = _repo_root() / path
    return full.read_text(encoding="utf-8", errors="ignore") if full.exists() else ""


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_server_json() -> dict[str, Any]:
    return _read_json(Path(".mcp") / "server.json")


def _overclaim_findings(paths: list[str] | None = None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    scan_paths = paths or ["README.md", "CHANGELOG.md", "docs/mcp_registry_pypi_path.md", "docs/mcp_registry_submission_gate.md", ".mcp/server.json"]
    negation = re.compile(r"\b(not|no|never|does not|do not|must not|is not|without|out of scope|outside scope)\b")
    for relative in scan_paths:
        text = _read_text(relative)
        for index, line in enumerate(text.splitlines(), start=1):
            lower = line.lower()
            for phrase in RISKY_PHRASES:
                if phrase in lower and not negation.search(lower):
                    findings.append({"path": relative, "line": index, "phrase": phrase})
    return findings


def _pypi_verified() -> bool:
    audit = _read_json(PYPI_RELEASE_AUDIT_PATH)
    return audit.get("decision") == "PASS_REAL_PYPI_RELEASE_VERIFIED"


def run_mcp_registry_manifest_final_audit(write_result: bool = True) -> dict[str, Any]:
    server = _read_server_json()
    packages = server.get("packages", []) if isinstance(server.get("packages"), list) else []
    package = packages[0] if packages and isinstance(packages[0], dict) else {}
    readme = _read_text("README.md")
    token_findings = tracked_token_findings()
    overclaims = _overclaim_findings()
    errors: list[str] = []
    warnings: list[str] = []

    checks = {
        "server_json_exists": bool(server),
        "server_name_matches": server.get("name") == MCP_NAME,
        "server_version_matches": server.get("version") == TARGET_VERSION,
        "registry_type_pypi": package.get("registryType") == "pypi",
        "package_identifier_matches": package.get("identifier") == PACKAGE_NAME,
        "package_version_matches": package.get("version") == TARGET_VERSION,
        "transport_stdio": (package.get("transport") or {}).get("type") == "stdio",
        "repository_public_url_matches": (server.get("repository") or {}).get("url") == GITHUB_REPO_URL,
        "readme_marker_matches": MCP_MARKER in readme,
        "pypi_release_verified": _pypi_verified(),
        "draft_not_submittable_false": server.get("draft_not_submittable") is not True,
    }
    if token_findings:
        errors.append("Tracked token-like content found.")
    if overclaims:
        errors.append("Positive overclaim wording found.")
    if not checks["pypi_release_verified"]:
        warnings.append("PyPI release audit has not confirmed the package.")
    if not checks["readme_marker_matches"]:
        warnings.append("README mcp-name marker is missing or mismatched.")
    missing_metadata = [name for name, ok in checks.items() if not ok and name not in {"pypi_release_verified", "readme_marker_matches"}]
    if missing_metadata:
        errors.append("server.json metadata mismatch: " + ", ".join(missing_metadata))

    if token_findings:
        decision = "BLOCK_SECRET_FINDING"
    elif overclaims:
        decision = "BLOCK_OVERCLAIM"
    elif missing_metadata:
        decision = "BLOCK_METADATA_MISMATCH"
    elif not checks["readme_marker_matches"]:
        decision = "HOLD_README_MARKER_MISSING"
    elif not checks["pypi_release_verified"]:
        decision = "HOLD_PYPI_NOT_VERIFIED"
    else:
        decision = "PASS_MANIFEST_READY"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "server_name": server.get("name"),
        "server_version": server.get("version"),
        "package": package,
        "repository_url": (server.get("repository") or {}).get("url"),
        "pypi_project_url": PYPI_PROJECT_URL,
        "checks": checks,
        "overclaim_findings": overclaims,
        "token_like_tracked_findings": token_findings,
        "mcp_registry_submission_performed": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_mcp_registry_manifest_final_audit()
    print(f"mcp_registry_manifest_final_audit: {result['decision']}")


if __name__ == "__main__":
    main()
