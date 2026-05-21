from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .real_pypi_upload_gate import TARGET_VERSION, _repo_root, check_pypi_project_status
from .real_pypi_upload_runner import OUTPUT_PATH as UPLOAD_RESULT_PATH, PYPI_PROJECT_URL


OUTPUT_PATH = Path("public_launch") / "wave10_real_pypi" / "REAL_PYPI_POST_UPLOAD_RECONCILE_RESULT.json"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def run_real_pypi_post_upload_reconcile(
    pypi_status_checker: Callable[[], dict[str, Any]] = check_pypi_project_status,
    write_result: bool = True,
) -> dict[str, Any]:
    status = pypi_status_checker()
    version_reachable = status.get("status") == "HOLD_VERSION_ALREADY_EXISTS" and TARGET_VERSION in status.get("versions", [])
    errors: list[str] = []
    warnings: list[str] = []

    if version_reachable:
        result_token = "UPLOAD_SUCCESS_DIRECT_TWINE_VERIFIED"
        upload_performed = True
        pypi_project_url = PYPI_PROJECT_URL
        next_action = "Run real PyPI install verification, release audit, and MCP Registry after-PyPI gate."
    else:
        result_token = "HOLD_DIRECT_TWINE_UPLOAD_NOT_VERIFIED"
        upload_performed = False
        pypi_project_url = ""
        next_action = "Wait briefly and rerun reconciliation, or check PyPI project/version manually."
        warnings.append("PyPI project/version was not confirmed by the public PyPI JSON endpoint.")

    upload_result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": False,
        "execute": False,
        "manual_direct_twine_upload": True,
        "env_confirm_present": False,
        "upload_performed": upload_performed,
        "command_redacted": "manual direct twine upload; token entered only in local twine prompt",
        "upload_result": {
            "ok": version_reachable,
            "pypi_status": status,
            "stdout": "[redacted: manual direct twine upload; PyPI version check used for confirmation]",
            "stderr": "",
        },
        "token_printed": False,
        "pypi_project_url": pypi_project_url,
        "result_token": result_token,
        "errors": errors,
        "warnings": warnings,
        "testpypi_used": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
    }
    reconcile_result = {
        "generated_at": upload_result["generated_at"],
        "pypi_version_reachable": version_reachable,
        "target_version": TARGET_VERSION,
        "pypi_status": status,
        "upload_result_token": result_token,
        "upload_result_path": str(UPLOAD_RESULT_PATH),
        "pypi_project_url": pypi_project_url,
        "token_printed": False,
        "next_action": next_action,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(UPLOAD_RESULT_PATH, upload_result)
        _write_json(OUTPUT_PATH, reconcile_result)
    return reconcile_result


def main() -> None:
    result = run_real_pypi_post_upload_reconcile()
    print(
        "real_pypi_post_upload_reconcile: "
        f"pypi_version_reachable={result['pypi_version_reachable']} "
        f"upload_result_token={result['upload_result_token']} "
        "token_printed=False"
    )


if __name__ == "__main__":
    main()
