from __future__ import annotations

import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


WAVE2_DIR = Path("public_launch") / "wave2"
OUTPUT_PATH = WAVE2_DIR / "PACKAGE_METADATA_AUDIT_RESULT.json"
MCP_NAME = "io.github.isometric-architect/ai-objective-index"
MCP_MARKER = f"<!-- mcp-name: {MCP_NAME} -->"
RECOMMENDED_VERSION = "0.3.0a1"

PEP440_SIMPLE = re.compile(r"^[0-9]+(?:\.[0-9]+)*(?:(?:a|b|rc)[0-9]+)?(?:\.post[0-9]+)?(?:\.dev[0-9]+)?$")
TOKEN_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]+"),
    re.compile(r"gho_[A-Za-z0-9_]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    re.compile(r"xoxb-[A-Za-z0-9-]+"),
    re.compile(r"api_key\s*=", re.IGNORECASE),
    re.compile(r"password\s*=", re.IGNORECASE),
    re.compile(r"PRIVATE KEY"),
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_pyproject() -> dict[str, Any]:
    path = _repo_root() / "pyproject.toml"
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    return payload if isinstance(payload, dict) else {}


def _read(path: str) -> str:
    full = _repo_root() / path
    return full.read_text(encoding="utf-8", errors="ignore") if full.exists() else ""


def version_is_pep440(version: str) -> bool:
    return bool(PEP440_SIMPLE.fullmatch(version))


def readme_has_mcp_marker(text: str, marker: str = MCP_MARKER) -> bool:
    return marker in text


def find_token_like_strings(text: str) -> list[str]:
    findings: list[str] = []
    for pattern in TOKEN_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern)
    return findings


def run_package_metadata_audit(write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    pyproject = _read_pyproject()
    project = pyproject.get("project", {}) if isinstance(pyproject.get("project"), dict) else {}
    scripts = project.get("scripts", {}) if isinstance(project.get("scripts"), dict) else {}
    optional_deps = project.get("optional-dependencies", {}) if isinstance(project.get("optional-dependencies"), dict) else {}
    readme = _read("README.md")
    pyproject_text = _read("pyproject.toml")
    version = str(project.get("version") or "")
    token_findings = find_token_like_strings(readme + "\n" + pyproject_text)
    claim_text = readme.lower()
    claim_boundaries = {
        "not_verified": "not verified" in claim_text,
        "not_security_certified": "not security certified" in claim_text,
        "not_quality_guarantee": "not a quality guarantee" in claim_text or "not quality guarantee" in claim_text,
    }
    checks = {
        "pyproject_exists": (root / "pyproject.toml").exists(),
        "project_name": project.get("name") == "ai-objective-index",
        "package_import_name": (root / "src/ai_objective_index").exists(),
        "version_pep440": version_is_pep440(version),
        "version_recommended": version == RECOMMENDED_VERSION,
        "license_exists": (root / "LICENSE").exists() or bool(project.get("license")),
        "readme_exists": (root / "README.md").exists(),
        "readme_mcp_marker": readme_has_mcp_marker(readme),
        "console_script_mcp": "ai-objective-index-mcp" in scripts,
        "console_script_smoke": "ai-objective-index-mcp-smoke" in scripts,
        "optional_mcp_dependency": "mcp" in optional_deps,
        "claim_boundaries": all(claim_boundaries.values()),
        "no_token_like_strings": not token_findings,
    }
    errors = [key for key, ok in checks.items() if not ok and key in {"pyproject_exists", "project_name", "package_import_name", "version_pep440", "license_exists", "readme_exists", "readme_mcp_marker", "no_token_like_strings"}]
    warnings = [key for key, ok in checks.items() if not ok and key not in errors]
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not errors else "BLOCK",
        "checks": checks,
        "project_name": project.get("name"),
        "package_import_name": "ai_objective_index",
        "version": version,
        "recommended_version": RECOMMENDED_VERSION,
        "mcp_name_marker": MCP_MARKER,
        "claim_boundaries": claim_boundaries,
        "token_like_findings": token_findings,
        "errors": errors,
        "warnings": warnings,
        "upload_performed": False,
        "mcp_registry_submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_package_metadata_audit()
    print(
        "package_metadata_audit: "
        f"{result['overall_token']} "
        f"version={result['version']} "
        f"mcp_marker={result['checks']['readme_mcp_marker']}"
    )


if __name__ == "__main__":
    main()
