from __future__ import annotations

import argparse
import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TARGET_VERSION = "0.3.0a1"
OUTPUT_PATH = Path("public_launch") / "wave9" / "VERSION_APPLY_RESULT.json"
PEP440_SIMPLE = re.compile(r"^[0-9]+(?:\.[0-9]+)*(?:(?:a|b|rc)[0-9]+)?(?:\.post[0-9]+)?(?:\.dev[0-9]+)?$")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_pyproject_version(root: Path | None = None) -> str:
    base = root or _repo_root()
    path = base / "pyproject.toml"
    if not path.exists():
        return ""
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    project = payload.get("project", {}) if isinstance(payload, dict) else {}
    return str(project.get("version") or "") if isinstance(project, dict) else ""


def _read_server_json(root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    path = base / ".mcp" / "server.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _replace_first(pattern: str, replacement: str, text: str) -> str:
    return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)


def _apply_pyproject_version(version: str, root: Path | None = None) -> None:
    base = root or _repo_root()
    path = base / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    text = _replace_first(r'^version = "[^"]+"', f'version = "{version}"', text)
    path.write_text(text, encoding="utf-8")


def _apply_init_version(version: str, root: Path | None = None) -> None:
    base = root or _repo_root()
    path = base / "src" / "ai_objective_index" / "__init__.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = _replace_first(r'^__version__ = "[^"]+"', f'__version__ = "{version}"', text)
    path.write_text(text, encoding="utf-8")


def _apply_server_json_version(version: str, root: Path | None = None) -> None:
    base = root or _repo_root()
    path = base / ".mcp" / "server.json"
    payload = _read_server_json(base)
    if not payload:
        return
    payload["version"] = version
    packages = payload.get("packages", [])
    if isinstance(packages, list):
        for package in packages:
            if isinstance(package, dict) and package.get("identifier") == "ai-objective-index":
                package["version"] = version
    payload["vnext_distribution_status"] = "VERSION_APPLIED_0_3_0A1"
    payload["pypi_upload_required"] = True
    payload["mcp_registry_submission_performed"] = False
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_version_apply_gate(
    apply_version: str | None = None,
    target_version: str = TARGET_VERSION,
    root: Path | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    base = root or _repo_root()
    old_pyproject = _read_pyproject_version(base)
    server = _read_server_json(base)
    old_server = str(server.get("version") or "")
    errors: list[str] = []
    warnings: list[str] = []
    applied = False

    requested = apply_version or target_version
    if requested and not PEP440_SIMPLE.fullmatch(requested):
        errors.append(f"Invalid PEP 440 version: {requested}")
    elif apply_version:
        _apply_pyproject_version(apply_version, base)
        _apply_init_version(apply_version, base)
        _apply_server_json_version(apply_version, base)
        applied = True

    new_pyproject = _read_pyproject_version(base)
    new_server = str(_read_server_json(base).get("version") or "")
    if apply_version and new_pyproject != apply_version:
        errors.append("pyproject.toml version did not update to the requested version.")
    if apply_version and new_server and new_server != apply_version:
        errors.append(".mcp/server.json version did not update to the requested version.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": apply_version is None,
        "apply": apply_version,
        "target_version": target_version,
        "old_pyproject_version": old_pyproject,
        "new_pyproject_version": new_pyproject,
        "old_server_json_version": old_server,
        "new_server_json_version": new_server,
        "version_changed": applied and old_pyproject != new_pyproject,
        "errors": errors,
        "warnings": warnings,
        "testpypi_upload_performed": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Apply or dry-run AOI vNext package version alignment.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", default=None, help="Version to apply, for example 0.3.0a1.")
    args = parser.parse_args(argv)
    result = run_version_apply_gate(apply_version=args.apply)
    print(
        "version_apply_gate: "
        f"dry_run={result['dry_run']} "
        f"old={result['old_pyproject_version']} "
        f"new={result['new_pyproject_version']} "
        f"errors={len(result['errors'])}"
    )


if __name__ == "__main__":
    main()
