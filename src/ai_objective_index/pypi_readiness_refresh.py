from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


WAVE2_DIR = Path("public_launch") / "wave2"
WAVE3_DIR = Path("public_launch") / "wave3"
OUTPUT_PATH = WAVE3_DIR / "PYPI_READINESS_REFRESH_RESULT.json"
SUMMARY_PATH = WAVE3_DIR / "PACKAGE_8Q_A_SUMMARY.md"
NEXT_STEPS_PATH = WAVE3_DIR / "NEXT_PYPI_ACCOUNT_STEPS.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_next_steps() -> Path:
    text = """# Next PyPI Account Steps

1. Create a TestPyPI account.
2. Verify your TestPyPI email.
3. Create a TestPyPI API token.
4. Do not paste the token into ChatGPT/Codex chat.
5. Use the token only in your terminal when `twine` asks.
6. After TestPyPI succeeds, create a real PyPI account and a separate PyPI token.
7. Upload to real PyPI only after the TestPyPI install test passes.

Notes:

- TestPyPI and PyPI are separate accounts.
- Token text may be visible only once.
- Keep tokens private.
- Do not commit `.pypirc` or token files.
- Package 8Q-A does not upload anything.
"""
    return _write(NEXT_STEPS_PATH, text)


def run_pypi_readiness_refresh(write_result: bool = True) -> dict[str, Any]:
    metadata = _read_json(WAVE2_DIR / "PACKAGE_METADATA_AUDIT_RESULT.json")
    wave2 = _read_json(WAVE2_DIR / "PYPI_PUBLISH_READINESS_RESULT.json")
    build = _read_json(WAVE3_DIR / "DIST_BUILD_RESULT.json")
    twine = _read_json(WAVE3_DIR / "TWINE_CHECK_RESULT.json")
    install = _read_json(WAVE3_DIR / "LOCAL_INSTALL_SMOKE_RESULT.json")
    errors: list[str] = []
    warnings: list[str] = []

    if metadata.get("overall_token") not in {"PASS", None} and metadata:
        decision = "BLOCK_INVALID_METADATA"
        errors.append("Package metadata audit did not pass.")
    elif build.get("decision") == "PASS_BUILD_READY" and twine.get("decision") == "PASS_TWINE_CHECK":
        if install.get("decision") == "PASS_LOCAL_INSTALL_SMOKE":
            decision = "HOLD_TESTPYPI_ACCOUNT_REQUIRED"
        else:
            decision = "HOLD_LOCAL_INSTALL_SMOKE_NOT_PASSING"
            warnings.append("Build and twine passed, but local install smoke did not fully pass.")
    elif build.get("decision") in {"HOLD_BUILD_TOOL_MISSING", ""} or wave2.get("decision") == "HOLD_BUILD_TOOL_MISSING":
        decision = "HOLD_BUILD_TOOL_MISSING"
        warnings.append("Build tooling or dist artifacts are still missing.")
    elif build.get("decision") == "HOLD_TWINE_MISSING":
        decision = "HOLD_TWINE_MISSING"
        warnings.append("Build passed but twine check is unavailable.")
    elif build.get("decision", "").startswith("BLOCK"):
        decision = build.get("decision")
        errors.append("Build or twine check failed.")
    else:
        decision = "HOLD_PYPI_UPLOAD_REQUIRED"
        warnings.append("Package is not yet uploaded to TestPyPI or PyPI.")

    dist_files = build.get("dist_files") or wave2.get("dist_files") or []
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "package_metadata_token": metadata.get("overall_token"),
        "wave2_decision": wave2.get("decision"),
        "dist_build_decision": build.get("decision"),
        "twine_check_decision": twine.get("decision"),
        "local_install_smoke_decision": install.get("decision"),
        "dist_files": dist_files,
        "next_required_step": "Create TestPyPI account/token and upload manually only after user approval." if decision == "HOLD_TESTPYPI_ACCOUNT_REQUIRED" else "Resolve the HOLD/BLOCK reason before upload.",
        "pypi_upload_performed": False,
        "testpypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write_next_steps()
        summary = f"""# Package 8Q-A Summary

Package 8Q-A installs/checks local build tooling, builds local distribution artifacts, runs `twine check`, runs a local install smoke where possible, and refreshes PyPI/MCP Registry readiness.

## Result

- PyPI readiness refresh decision: `{decision}`
- Dist files: {len(dist_files)}
- TestPyPI upload performed: false
- PyPI upload performed: false
- MCP Registry submission performed: false
- Token printed: false

Next step: {result['next_required_step']}
"""
        _write(SUMMARY_PATH, summary)
    return result


def main() -> None:
    result = run_pypi_readiness_refresh()
    print(
        "pypi_readiness_refresh: "
        f"{result['decision']} "
        f"dist_files={len(result['dist_files'])} "
        "upload_performed=False"
    )


if __name__ == "__main__":
    main()
