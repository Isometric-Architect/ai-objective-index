from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_install_verify import OUTPUT_PATH as INSTALL_RESULT_PATH
from .real_pypi_upload_gate import TARGET_VERSION, _repo_root, tracked_token_findings
from .real_pypi_upload_runner import OUTPUT_PATH as UPLOAD_RESULT_PATH, PYPI_PROJECT_URL


OUTPUT_PATH = Path("public_launch") / "wave10_real_pypi" / "REAL_PYPI_RELEASE_AUDIT_RESULT.json"
SUMMARY_PATH = Path("public_launch") / "wave10_real_pypi" / "PACKAGE_8Q_C_ALT_REAL_PYPI_SUMMARY.md"
RISKY_PHRASES = [
    "verified capability",
    "safe tool",
    "security certified",
    "quality guaranteed",
    "production ready",
    "production-ready",
    "purchase recommendation",
    "legal advice",
]


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


def _scan_overclaims() -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for relative in ["README.md", "CHANGELOG.md", "docs/pypi_publish_readiness.md", "docs/mcp_registry_pypi_path.md"]:
        path = _repo_root() / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        lines = text.splitlines()
        for phrase in RISKY_PHRASES:
            for line in lines:
                if phrase not in line:
                    continue
                if any(marker in line for marker in ["not ", "no ", "does not", "do not claim", "never "]):
                    continue
                findings.append({"path": relative, "phrase": phrase})
    return findings


def run_real_pypi_release_audit(write_result: bool = True) -> dict[str, Any]:
    upload = _read_json(UPLOAD_RESULT_PATH)
    install = _read_json(INSTALL_RESULT_PATH)
    token_findings = tracked_token_findings()
    overclaims = _scan_overclaims()
    errors: list[str] = []
    warnings: list[str] = []

    upload_confirmed = upload.get("result_token") in {"UPLOAD_SUCCESS", "HOLD_ALREADY_EXISTS"}
    install_passed = install.get("decision") == "PASS_REAL_PYPI_INSTALL"
    if token_findings:
        decision = "BLOCK_TOKEN_FINDING"
        errors.append("Tracked token-like content found.")
    elif overclaims:
        decision = "BLOCK_OVERCLAIM"
        errors.append("Positive overclaim wording found.")
    elif not upload_confirmed:
        decision = "HOLD_UPLOAD_NOT_CONFIRMED"
        warnings.append("Real PyPI upload has not been confirmed.")
    elif not install_passed:
        decision = "HOLD_INSTALL_VERIFY_REQUIRED"
        warnings.append("Real PyPI install verification has not passed.")
    else:
        decision = "PASS_REAL_PYPI_RELEASE_VERIFIED"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "upload_result_token": upload.get("result_token"),
        "install_verify_decision": install.get("decision"),
        "pypi_project_url": upload.get("pypi_project_url") or PYPI_PROJECT_URL if upload_confirmed else "",
        "token_like_tracked_findings": token_findings,
        "overclaim_findings": overclaims,
        "mcp_registry_submission_performed": False,
        "testpypi_used": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write(
            SUMMARY_PATH,
            f"""# Package 8Q-C-alt Real PyPI Summary

Package 8Q-C-alt adds a strict real PyPI direct upload gate because TestPyPI signup is blocked for the owner.

## Current Result

- Upload gate / upload result: `{upload.get('result_token') or 'not_run'}`
- Real PyPI install verification: `{install.get('decision') or 'not_run'}`
- Release audit: `{decision}`
- TestPyPI used: false
- MCP Registry submission performed: false
- Community posting performed: false
- Token printed: false

PyPI project URL, after successful upload: {result['pypi_project_url'] or 'not confirmed yet'}

AOI remains a read-only, source-traced capability routing prototype. The PyPI package is not a verification, security certification, quality guarantee, product-readiness claim, or purchasing advice.
""",
        )
    return result


def main() -> None:
    result = run_real_pypi_release_audit()
    print(
        "real_pypi_release_audit: "
        f"{result['decision']} "
        "mcp_registry_submission_performed=False"
    )


if __name__ == "__main__":
    main()
