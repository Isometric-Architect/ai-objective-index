from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_registry_submit_reconcile import OUTPUT_PATH as RECONCILE_PATH
from .package_metadata_audit import MCP_NAME
from .real_pypi_upload_gate import PACKAGE_NAME, TARGET_VERSION, _repo_root


OUTPUT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_REGISTRY_DISCOVERY_REPORT.json"
MONITORING_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_REGISTRY_POST_SUBMIT_MONITORING.md"
SUMMARY_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "PACKAGE_8R_B_MCP_REGISTRY_SUBMIT_SUMMARY.md"
GITHUB_URL = "https://github.com/Isometric-Architect/ai-objective-index"
PYPI_URL = "https://pypi.org/project/ai-objective-index/0.3.0a1/"


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


def run_mcp_registry_discovery_report(write_result: bool = True) -> dict[str, Any]:
    reconcile = _read_json(RECONCILE_PATH)
    status = reconcile.get("decision") or "NOT_CHECKED"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "server_name": MCP_NAME,
        "registry_status": status,
        "pypi_package": {"identifier": PACKAGE_NAME, "version": TARGET_VERSION, "url": PYPI_URL},
        "github_repo": GITHUB_URL,
        "claim_boundary": [
            "not verified",
            "not security certified",
            "not a quality guarantee",
            "read-only/local metadata routing",
            "no payment/booking/login/email/purchase/contract actions",
        ],
        "next_monitoring": ["search visibility", "install path", "issue reports", "no immediate traffic is not failure"],
        "mcp_registry_submission_performed": bool(reconcile.get("mcp_registry_submission_performed")),
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write(
            MONITORING_PATH,
            f"""# MCP Registry Post-Submit Monitoring

- Server name: `{MCP_NAME}`
- Registry status: `{status}`
- PyPI: {PYPI_URL}
- GitHub: {GITHUB_URL}

## Claim Boundary

- Not verified
- Not security certified
- Not a quality guarantee
- Read-only/local metadata routing
- No payment, booking, login, email, purchase, or contract actions

## Monitor

- Search visibility
- Install path
- Issue reports
- No immediate traffic is not failure
""",
        )
        _write(
            SUMMARY_PATH,
            f"""# Package 8R-B MCP Registry Submit Summary

- Server name: `{MCP_NAME}`
- Package: `{PACKAGE_NAME}=={TARGET_VERSION}`
- Registry status: `{status}`
- Submission performed: {str(bool(reconcile.get('mcp_registry_submission_performed'))).lower()}
- PyPI: {PYPI_URL}
- GitHub: {GITHUB_URL}

Registry publication is not verification, security certification, a quality guarantee, product-readiness evidence, purchasing advice, or action authorization.
""",
        )
    return result


def main() -> None:
    result = run_mcp_registry_discovery_report()
    print(f"mcp_registry_discovery_report: {result['registry_status']}")


if __name__ == "__main__":
    main()
