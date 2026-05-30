from __future__ import annotations

import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path("public_launch") / "aoi_030a2_registry_recovery"
OUTPUT_PATH = OUTPUT_DIR / "AOI_030A2_MARKER_SYNC_RESULT.json"
PACKAGE_NAME = "ai-objective-index"
IMPORT_NAME = "ai_objective_index"
CANONICAL_MCP_NAME = "io.github.Isometric-Architect/ai-objective-index"
MCP_MARKER = f"<!-- mcp-name: {CANONICAL_MCP_NAME} -->"
PREVIOUS_VERSION = "0.3.0a1"
TARGET_VERSION = "0.3.0a2"
WHEEL_PATH = Path("dist") / f"ai_objective_index-{TARGET_VERSION}-py3-none-any.whl"
SDIST_PATH = Path("dist") / f"ai_objective_index-{TARGET_VERSION}.tar.gz"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def read_json(path: Path) -> dict[str, Any]:
    full = repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def read_text(path: Path) -> str:
    full = repo_root() / path
    return full.read_text(encoding="utf-8", errors="ignore") if full.exists() else ""


def _read_pyproject() -> dict[str, Any]:
    path = repo_root() / "pyproject.toml"
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    return payload if isinstance(payload, dict) else {}


def _extract_init_version(text: str) -> str:
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
    return match.group(1) if match else ""


def _extract_readme_marker(text: str) -> str:
    match = re.search(r"<!--\s*mcp-name:\s*([^>]+?)\s*-->", text)
    return match.group(1).strip() if match else ""


def _previous_package_marker() -> dict[str, Any]:
    candidates = [
        Path("src") / "ai_objective_index.egg-info" / "PKG-INFO",
        Path("dist") / f"ai_objective_index-{PREVIOUS_VERSION}.tar.gz",
    ]
    for path in candidates:
        text = read_text(path)
        marker = _extract_readme_marker(text)
        if marker:
            return {"source": str(path), "inspectable": True, "marker": marker, "matches": marker == CANONICAL_MCP_NAME}
    return {"source": "", "inspectable": False, "marker": "", "matches": False}


def current_marker_state() -> dict[str, Any]:
    pyproject = _read_pyproject()
    project = pyproject.get("project", {}) if isinstance(pyproject.get("project"), dict) else {}
    init_text = read_text(Path("src") / "ai_objective_index" / "__init__.py")
    server = read_json(Path(".mcp") / "server.json")
    packages = server.get("packages", []) if isinstance(server.get("packages"), list) else []
    package = packages[0] if packages and isinstance(packages[0], dict) else {}
    readme = read_text(Path("README.md"))
    return {
        "pyproject_version": str(project.get("version") or ""),
        "init_version": _extract_init_version(init_text),
        "server_name": str(server.get("name") or ""),
        "server_version": str(server.get("version") or ""),
        "server_package_registry_type": str(package.get("registryType") or ""),
        "server_package_identifier": str(package.get("identifier") or ""),
        "server_package_version": str(package.get("version") or ""),
        "readme_mcp_name": _extract_readme_marker(readme),
        "readme_marker_present": MCP_MARKER in readme,
        "previous_pypi_030a1_marker": _previous_package_marker(),
    }


def sync_needed(state: dict[str, Any] | None = None) -> list[str]:
    state = state or current_marker_state()
    checks = {
        "pyproject_version": state.get("pyproject_version") == TARGET_VERSION,
        "init_version": state.get("init_version") == TARGET_VERSION,
        "server_name": state.get("server_name") == CANONICAL_MCP_NAME,
        "server_version": state.get("server_version") == TARGET_VERSION,
        "server_package_registry_type": state.get("server_package_registry_type") == "pypi",
        "server_package_identifier": state.get("server_package_identifier") == PACKAGE_NAME,
        "server_package_version": state.get("server_package_version") == TARGET_VERSION,
        "readme_marker": state.get("readme_mcp_name") == CANONICAL_MCP_NAME,
    }
    return [key for key, ok in checks.items() if not ok]


def _replace_text(path: Path, replacements: list[tuple[str, str]]) -> bool:
    full = repo_root() / path
    text = full.read_text(encoding="utf-8")
    new_text = text
    for pattern, replacement in replacements:
        new_text = re.sub(pattern, replacement, new_text, count=1, flags=re.MULTILINE)
    if new_text != text:
        full.write_text(new_text, encoding="utf-8")
        return True
    return False


def apply_030a2_sync() -> list[str]:
    changed: list[str] = []
    if _replace_text(Path("pyproject.toml"), [(r'^version = "[^"]+"', f'version = "{TARGET_VERSION}"')]):
        changed.append("pyproject.toml")
    if _replace_text(
        Path("src") / "ai_objective_index" / "__init__.py",
        [(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{TARGET_VERSION}"')],
    ):
        changed.append("src/ai_objective_index/__init__.py")

    server_path = Path(".mcp") / "server.json"
    server = read_json(server_path)
    if server:
        before = json.dumps(server, sort_keys=True)
        server["name"] = CANONICAL_MCP_NAME
        server["version"] = TARGET_VERSION
        packages = server.get("packages", []) if isinstance(server.get("packages"), list) else []
        if packages and isinstance(packages[0], dict):
            packages[0]["registryType"] = "pypi"
            packages[0]["identifier"] = PACKAGE_NAME
            packages[0]["version"] = TARGET_VERSION
        server["draft_reason"] = (
            "Real PyPI package 0.3.0a2 is the marker-sync recovery target for MCP Registry submission; "
            "publication remains gated by PyPI verification, mcp-publisher, GitHub auth, and explicit confirmation."
        )
        server["generated_at"] = datetime.now(UTC).isoformat()
        if json.dumps(server, sort_keys=True) != before:
            (repo_root() / server_path).write_text(json.dumps(server, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed.append(".mcp/server.json")

    readme_path = Path("README.md")
    readme = read_text(readme_path)
    if "<!-- mcp-name:" in readme:
        new_readme = re.sub(r"<!--\s*mcp-name:\s*[^>]+?-->", MCP_MARKER, readme, count=1)
    else:
        new_readme = f"# AI Objective Index\n{MCP_MARKER}\n" + re.sub(r"^# AI Objective Index\s*", "", readme, count=1)
    if new_readme != readme:
        (repo_root() / readme_path).write_text(new_readme, encoding="utf-8")
        changed.append("README.md")
    return changed


def run_marker_sync(apply: bool = False, write_result: bool = True) -> dict[str, Any]:
    before = current_marker_state()
    changed = apply_030a2_sync() if apply else []
    after = current_marker_state()
    missing = sync_needed(after)
    decision = "PASS_MARKER_SYNCED_030A2" if not missing else "HOLD_MARKER_SYNC_REQUIRED"
    result = {
        "schema": "AOI_030A2MarkerSyncResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "canonical_mcp_name": CANONICAL_MCP_NAME,
        "package": {"registryType": "pypi", "identifier": PACKAGE_NAME, "version": TARGET_VERSION},
        "before": before,
        "after": after,
        "changed_files": changed,
        "missing_or_mismatched": missing,
        "token_printed": False,
        "upload_performed": False,
        "mcp_registry_submission_performed": False,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_marker_sync(apply=False)
    print(f"aoi_030a2_marker_sync: {result['decision']} missing={len(result['missing_or_mismatched'])}")


if __name__ == "__main__":
    main()
