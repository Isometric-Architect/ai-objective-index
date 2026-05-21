from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_registry_manifest_final_audit import OUTPUT_PATH as MANIFEST_AUDIT_PATH, run_mcp_registry_manifest_final_audit
from .mcp_registry_post_publish_verify import OUTPUT_PATH as VERIFY_PATH
from .mcp_registry_publish_runner import OUTPUT_PATH as PUBLISH_PATH
from .real_pypi_release_audit import OUTPUT_PATH as PYPI_RELEASE_AUDIT_PATH
from .real_pypi_upload_gate import _repo_root, tracked_token_findings


OUTPUT_PATH = Path("public_launch") / "wave11_mcp_registry" / "MCP_REGISTRY_RELEASE_AUDIT_RESULT.json"
SUMMARY_PATH = Path("public_launch") / "wave11_mcp_registry" / "PACKAGE_8R_MCP_REGISTRY_SUMMARY.md"


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


def _claim_guard_passed() -> bool:
    path = _repo_root() / "data" / "generated" / "launch_claim_guard_result_v0_2.json"
    if not path.exists():
        return True
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("overall_token") == "PASS" or payload.get("risky_phrase_count") == 0


def run_mcp_registry_release_audit(write_result: bool = True) -> dict[str, Any]:
    publish = _read_json(PUBLISH_PATH)
    verify = _read_json(VERIFY_PATH)
    manifest = _read_json(MANIFEST_AUDIT_PATH) or run_mcp_registry_manifest_final_audit(write_result=False)
    pypi_release = _read_json(PYPI_RELEASE_AUDIT_PATH)
    token_findings = tracked_token_findings()
    errors: list[str] = []
    warnings: list[str] = []

    if token_findings:
        decision = "BLOCK_SECRET_FINDING"
        errors.append("Tracked token-like content found.")
    elif not _claim_guard_passed() or manifest.get("decision") == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
        errors.append("Claim guard or manifest audit found overclaim wording.")
    elif publish.get("result_token") != "PUBLISH_SUCCESS" or not publish.get("submission_performed"):
        decision = "HOLD_PUBLISH_NOT_CONFIRMED"
        warnings.append("MCP Registry publish has not been confirmed.")
    elif verify.get("decision") != "PASS_REGISTRY_ENTRY_FOUND":
        decision = "HOLD_VERIFY_NOT_FOUND_YET"
        warnings.append("MCP Registry entry has not been found by post-publish verification.")
    else:
        decision = "PASS_MCP_REGISTRY_RELEASE_RECORDED"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "publish_result_token": publish.get("result_token"),
        "submission_performed": bool(publish.get("submission_performed")),
        "post_publish_verify_decision": verify.get("decision"),
        "manifest_audit_decision": manifest.get("decision"),
        "pypi_release_audit_decision": pypi_release.get("decision"),
        "token_like_tracked_findings": token_findings,
        "mcp_registry_submission_performed": bool(publish.get("submission_performed")),
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write(
            SUMMARY_PATH,
            f"""# Package 8R MCP Registry Summary

Package 8R prepares AI Objective Index for Official MCP Registry publication after the real PyPI upload.

## Results

- Manifest final audit: `{manifest.get('decision') or 'not_run'}`
- Publish result: `{publish.get('result_token') or 'not_run'}`
- Registry verify: `{verify.get('decision') or 'not_run'}`
- Release audit: `{decision}`
- Submission performed: {str(bool(publish.get('submission_performed'))).lower()}
- Token printed: false

Registry publication, if later completed, is a metadata listing only. It is not security certification, a quality guarantee, product-readiness evidence, purchasing advice, or action authorization.
""",
        )
    return result


def main() -> None:
    result = run_mcp_registry_release_audit()
    print(f"mcp_registry_release_audit: {result['decision']}")


if __name__ == "__main__":
    main()
