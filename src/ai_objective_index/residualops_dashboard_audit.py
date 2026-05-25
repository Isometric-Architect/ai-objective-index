from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_artifact_manifest import MANIFEST_PATH, OUTPUT_DIR
from .residualops_dashboard import DASHBOARD_JSON_PATH
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit


AUDIT_PATH = OUTPUT_DIR / "ROE2_DASHBOARD_AUDIT.json"


def _write_json(path: Path, payload: dict[str, Any], root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def run_dashboard_audit(write_result: bool = True, root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    manifest = _read_json(base / MANIFEST_PATH)
    dashboard = _read_json(base / DASHBOARD_JSON_PATH)
    alignment = run_public_private_alignment_audit(write_result=False, root=base, paths=[Path("docs"), Path("public_launch") / "roe2"])
    issues: list[str] = []
    if not manifest:
        issues.append("shared artifact manifest missing")
    if not dashboard:
        issues.append("vertical dashboard missing")
    if manifest.get("missing_artifacts"):
        issues.append("manifest has missing artifacts")
    for flag in ["external_actions_performed", "workflow_enabled", "network_used", "token_printed"]:
        if manifest.get(flag) or dashboard.get(flag):
            issues.append(f"{flag} unexpectedly true")
    if alignment["decision"] != "PASS_PUBLIC_PRIVATE_ALIGNMENT":
        issues.append(f"public/private alignment {alignment['decision']}")

    if any(issue.endswith("unexpectedly true") for issue in issues):
        decision = "BLOCK_EXTERNAL_ACTION_FLAG"
    elif alignment["decision"] == "BLOCK_PUBLIC_PRIVATE_LEAK":
        decision = "BLOCK_PUBLIC_PRIVATE_LEAK"
    elif alignment["decision"] == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
    elif issues:
        decision = "HOLD_ROE2_DASHBOARD_REVIEW"
    else:
        decision = "PASS_ROE2_DASHBOARD_AUDIT"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "issues": issues,
        "manifest_decision": manifest.get("decision"),
        "dashboard_decision": dashboard.get("decision"),
        "public_private_alignment_decision": alignment["decision"],
        "risky_phrase_count": alignment["risky_phrase_count"],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(AUDIT_PATH, result, root=base)
    return result


def main() -> None:
    result = run_dashboard_audit()
    print(f"residualops_dashboard_audit: {result['decision']} issues={len(result['issues'])}")


if __name__ == "__main__":
    main()
