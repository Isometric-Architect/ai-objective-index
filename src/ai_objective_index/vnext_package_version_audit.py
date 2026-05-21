from __future__ import annotations

import argparse
import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("public_launch") / "wave8" / "VNEXT_PACKAGE_VERSION_AUDIT.json"
RECOMMENDED_VERSION = "0.3.0"
RECOMMENDED_PRERELEASE_VERSION = "0.3.0a1"
PEP440_SIMPLE = re.compile(r"^[0-9]+(?:\.[0-9]+)*(?:(?:a|b|rc)[0-9]+)?(?:\.post[0-9]+)?(?:\.dev[0-9]+)?$")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_pyproject() -> dict[str, Any]:
    path = _repo_root() / "pyproject.toml"
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _read_server_json() -> dict[str, Any]:
    path = _repo_root() / ".mcp" / "server.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _apply_pyproject_version(version: str) -> None:
    path = _repo_root() / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^version = "[^"]+"', f'version = "{version}"', text, count=1)
    path.write_text(text, encoding="utf-8")


def _apply_server_json_version(version: str) -> None:
    path = _repo_root() / ".mcp" / "server.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["version"] = version
    for package in payload.get("packages", []) if isinstance(payload.get("packages"), list) else []:
        if isinstance(package, dict) and package.get("identifier") == "ai-objective-index":
            package["version"] = version
    payload["vnext_distribution_status"] = "VERSION_APPLIED"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_vnext_package_version_audit(apply_version: str | None = None, write_result: bool = True) -> dict[str, Any]:
    pyproject = _read_pyproject()
    project = pyproject.get("project", {}) if isinstance(pyproject.get("project"), dict) else {}
    current_version = str(project.get("version") or "")
    server = _read_server_json()
    server_version = str(server.get("version") or "")
    version_change_applied = False
    errors: list[str] = []
    warnings: list[str] = []
    if apply_version:
        if not PEP440_SIMPLE.fullmatch(apply_version):
            errors.append(f"Requested version is not PEP 440-compatible: {apply_version}")
        else:
            _apply_pyproject_version(apply_version)
            _apply_server_json_version(apply_version)
            current_version = apply_version
            server_version = apply_version
            version_change_applied = True
    if not current_version:
        errors.append("pyproject version is missing.")
    if current_version and not PEP440_SIMPLE.fullmatch(current_version):
        errors.append("pyproject version is not PEP 440-compatible.")
    version_selected = current_version in {RECOMMENDED_VERSION, RECOMMENDED_PRERELEASE_VERSION} and (
        not server_version or server_version == current_version
    )
    if current_version == "0.2.0":
        warnings.append("vNext 9A-9E surfaces are present while pyproject version remains 0.2.0.")
    if server_version and server_version != current_version:
        warnings.append("server.json version differs from pyproject version.")
    if errors:
        decision = "BLOCK_INVALID_VERSION"
    elif version_change_applied:
        decision = "PASS_VERSION_APPLIED"
    elif version_selected:
        decision = "PASS_VERSION_SELECTED"
    else:
        decision = "HOLD_VERSION_DECISION"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "overall_token": "BLOCK" if decision.startswith("BLOCK") else ("PASS" if decision in {"PASS_VERSION_APPLIED", "PASS_VERSION_SELECTED"} else "HOLD"),
        "current_pyproject_version": current_version,
        "current_server_json_version": server_version,
        "recommended_version": RECOMMENDED_VERSION,
        "recommended_prerelease_version": RECOMMENDED_PRERELEASE_VERSION,
        "version_change_applied": version_change_applied,
        "reason": "AOI vNext 9A-9E added major public surfaces; choose 0.3.0 or 0.3.0a1 before PyPI upload.",
        "errors": errors,
        "warnings": warnings,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit vNext package version readiness.")
    parser.add_argument("--apply-version", default=None)
    args = parser.parse_args()
    result = run_vnext_package_version_audit(apply_version=args.apply_version)
    print(
        "vnext_package_version_audit: "
        f"{result['decision']} current={result['current_pyproject_version']} "
        f"recommended={result['recommended_version']} applied={result['version_change_applied']}"
    )


if __name__ == "__main__":
    main()
