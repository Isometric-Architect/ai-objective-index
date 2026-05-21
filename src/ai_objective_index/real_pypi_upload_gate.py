from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


PACKAGE_NAME = "ai-objective-index"
IMPORT_NAME = "ai_objective_index"
TARGET_VERSION = "0.3.0a1"
WHEEL_PATH = Path("dist") / "ai_objective_index-0.3.0a1-py3-none-any.whl"
SDIST_PATH = Path("dist") / "ai_objective_index-0.3.0a1.tar.gz"
OUTPUT_PATH = Path("public_launch") / "wave10_real_pypi" / "REAL_PYPI_UPLOAD_GATE_RESULT.json"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"

TOKEN_PATTERNS = [
    re.compile(r"pypi-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"gho_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
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


def _read_server_json() -> dict[str, Any]:
    path = _repo_root() / ".mcp" / "server.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _import_version() -> str:
    try:
        module = __import__(IMPORT_NAME)
    except Exception:
        return ""
    return str(getattr(module, "__version__", ""))


def _sanitize(value: Any) -> str:
    text = str(value or "")
    for pattern in TOKEN_PATTERNS:
        text = pattern.sub("[redacted]", text)
    return text[:1600]


def run_twine_check_now() -> dict[str, Any]:
    command = [sys.executable, "-m", "twine", "check", str(WHEEL_PATH), str(SDIST_PATH)]
    try:
        completed = subprocess.run(
            command,
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=180,
            check=False,
        )
        return {
            "command": command,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def tracked_token_findings() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-c", "safe.directory=C:/Users/Isometric-Architect/Desktop/ai_objective_index", "ls-files"],
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return []
    findings: list[str] = []
    for raw in completed.stdout.splitlines():
        path = _repo_root() / raw
        if not path.exists() or path.is_dir() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        # Existing tests contain fake token-like fixtures to verify redaction.
        # Those are intentionally committed and covered by no_secrets_audit; do not
        # block the PyPI gate on those controlled test strings.
        normalized = raw.replace("\\", "/")
        if normalized.startswith("tests/") and ("redacts_token_like" in text or "REDACTED_TOKEN_LIKE_TEXT" in text):
            continue
        if any(pattern.search(text) for pattern in TOKEN_PATTERNS):
            findings.append(raw)
    return findings


def check_pypi_project_status(timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(PYPI_JSON_URL, headers={"User-Agent": "ai-objective-index-release-gate"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"status": "PROJECT_AVAILABLE_OR_NEW", "checked": True, "url": PYPI_JSON_URL, "versions": []}
        return {"status": "HOLD_PYPI_STATUS_NOT_CHECKED", "checked": False, "url": PYPI_JSON_URL, "error": f"HTTP {exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeError) as exc:
        return {"status": "HOLD_PYPI_STATUS_NOT_CHECKED", "checked": False, "url": PYPI_JSON_URL, "error": _sanitize(exc)}

    info = payload.get("info", {}) if isinstance(payload, dict) else {}
    releases = payload.get("releases", {}) if isinstance(payload, dict) else {}
    versions = sorted(str(item) for item in releases) if isinstance(releases, dict) else []
    normalized_name = str(info.get("name") or "").lower().replace("_", "-")
    if normalized_name and normalized_name != PACKAGE_NAME:
        return {"status": "BLOCK_PROJECT_NAME_TAKEN", "checked": True, "url": PYPI_JSON_URL, "name": info.get("name"), "versions": versions}
    if TARGET_VERSION in versions:
        return {"status": "HOLD_VERSION_ALREADY_EXISTS", "checked": True, "url": PYPI_JSON_URL, "name": info.get("name"), "versions": versions}
    return {
        "status": "HOLD_PROJECT_EXISTS_REVIEW_REQUIRED",
        "checked": True,
        "url": PYPI_JSON_URL,
        "name": info.get("name"),
        "versions": versions,
    }


def evaluate_real_pypi_upload_gate(
    pypi_status_checker: Callable[[], dict[str, Any]] = check_pypi_project_status,
    twine_checker: Callable[[], dict[str, Any]] = run_twine_check_now,
    token_scanner: Callable[[], list[str]] = tracked_token_findings,
    write_result: bool = True,
) -> dict[str, Any]:
    pyproject = _read_pyproject()
    project = pyproject.get("project", {}) if isinstance(pyproject.get("project"), dict) else {}
    server = _read_server_json()
    packages = server.get("packages", []) if isinstance(server.get("packages"), list) else []
    package = packages[0] if packages and isinstance(packages[0], dict) else {}
    wheel_exists = (_repo_root() / WHEEL_PATH).exists()
    sdist_exists = (_repo_root() / SDIST_PATH).exists()
    twine = twine_checker() if wheel_exists and sdist_exists else {"ok": False, "skipped": True}
    pypirc_exists = (_repo_root() / ".pypirc").exists()
    token_findings = token_scanner()
    pypi_status = pypi_status_checker()
    errors: list[str] = []
    warnings: list[str] = []

    if project.get("name") != PACKAGE_NAME:
        errors.append("pyproject package name mismatch.")
    if project.get("version") != TARGET_VERSION or server.get("version") != TARGET_VERSION or _import_version() != TARGET_VERSION:
        errors.append("Package versions are not all 0.3.0a1.")
    if package.get("registryType") != "pypi" or package.get("identifier") != PACKAGE_NAME:
        errors.append("server.json PyPI package metadata mismatch.")
    if not wheel_exists or not sdist_exists:
        warnings.append("Required dist wheel/sdist missing.")
    if not twine.get("ok"):
        warnings.append("twine check did not pass.")
    if pypirc_exists or token_findings:
        errors.append("Token file or token-like tracked content found.")
    if pypi_status.get("status") == "BLOCK_PROJECT_NAME_TAKEN":
        errors.append("PyPI project name appears taken by another project.")

    if errors and any("Token" in item or "token" in item for item in errors):
        decision = "BLOCK_TOKEN_FILE_FOUND"
    elif errors and any("version" in item.lower() for item in errors):
        decision = "BLOCK_VERSION_MISMATCH"
    elif errors and any("taken" in item.lower() for item in errors):
        decision = "BLOCK_PROJECT_NAME_TAKEN"
    elif errors:
        decision = "BLOCK_VERSION_MISMATCH"
    elif not wheel_exists or not sdist_exists:
        decision = "HOLD_DIST_MISSING"
    elif not twine.get("ok"):
        decision = "HOLD_TWINE_CHECK_REQUIRED"
    elif pypi_status.get("status") == "PROJECT_AVAILABLE_OR_NEW":
        decision = "PASS_READY_FOR_REAL_PYPI_UPLOAD"
    elif pypi_status.get("status") == "HOLD_VERSION_ALREADY_EXISTS":
        decision = "HOLD_VERSION_ALREADY_EXISTS"
    elif pypi_status.get("status") == "HOLD_PROJECT_EXISTS_REVIEW_REQUIRED":
        decision = "HOLD_PROJECT_EXISTS_REVIEW_REQUIRED"
    else:
        decision = "HOLD_PYPI_STATUS_NOT_CHECKED"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "package_name": project.get("name"),
        "target_version": TARGET_VERSION,
        "pyproject_version": project.get("version"),
        "server_json_version": server.get("version"),
        "import_version": _import_version(),
        "wheel_exists": wheel_exists,
        "sdist_exists": sdist_exists,
        "twine_check": twine,
        "pypirc_exists": pypirc_exists,
        "token_like_tracked_findings": token_findings,
        "pypi_status": pypi_status,
        "errors": errors,
        "warnings": warnings,
        "testpypi_used": False,
        "upload_performed": False,
        "mcp_registry_submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = evaluate_real_pypi_upload_gate()
    print(
        "real_pypi_upload_gate: "
        f"{result['decision']} "
        f"wheel={result['wheel_exists']} "
        f"sdist={result['sdist_exists']} "
        "upload_performed=False"
    )


if __name__ == "__main__":
    main()
