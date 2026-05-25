from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_artifact_manifest import (
    MANIFEST_PATH,
    OUTPUT_DIR,
    build_shared_artifact_manifest,
    _write_json,
)


DASHBOARD_JSON_PATH = OUTPUT_DIR / "ROE2_VERTICAL_STATUS_DASHBOARD.json"
DASHBOARD_MD_PATH = OUTPUT_DIR / "ROE2_VERTICAL_STATUS_DASHBOARD.md"
SUMMARY_PATH = OUTPUT_DIR / "ROE2_SUMMARY.md"
NEXT_STEPS_PATH = OUTPUT_DIR / "ROE2_NEXT_STEPS.md"


def _write_text(path: Path, text: str, root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _load_manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST_PATH
    if not path.exists():
        return build_shared_artifact_manifest(root=root)
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else build_shared_artifact_manifest(root=root)


def _status_from_bucket(bucket: str) -> str:
    if bucket == "allow":
        return "ALLOW_OR_PASS"
    if bucket == "hold":
        return "HOLD_REVIEW"
    if bucket == "block":
        return "BLOCK_RISK"
    return "UNKNOWN"


def build_vertical_status_dashboard(root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    manifest = _load_manifest(base)
    rows: list[dict[str, Any]] = []
    totals = {"allow": 0, "hold": 0, "block": 0}
    for vertical in manifest.get("verticals", []):
        counts = vertical.get("decision_counts", {})
        for key in totals:
            totals[key] += int(counts.get(key, 0) or 0)
        rows.append(
            {
                "vertical_id": vertical["vertical_id"],
                "product_name": vertical["product_name"],
                "package": vertical["package"],
                "status": _status_from_bucket(vertical["decision_bucket"]),
                "primary_decision": vertical["primary_decision"],
                "artifact_count": len(vertical.get("artifacts", [])),
                "missing_artifact_count": len([item for item in vertical.get("artifacts", []) if not item.get("exists")]),
                "safe_flags": vertical.get("safe_flags", {}),
                "dashboard_note": "local artifact status only; not certification or action authorization",
            }
        )
    block_count = len([row for row in rows if row["status"] == "BLOCK_RISK"])
    hold_count = len([row for row in rows if row["status"] == "HOLD_REVIEW"])
    decision = "PASS_ROE2_DASHBOARD_READY" if manifest.get("decision") == "PASS_ROE2_SHARED_MANIFEST_READY" else "HOLD_ROE2_DASHBOARD_INCOMPLETE"
    return {
        "schema": "ResidualOps_VerticalStatusDashboard/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "manifest_decision": manifest.get("decision"),
        "vertical_count": len(rows),
        "status_counts": {
            "allow_or_pass": len([row for row in rows if row["status"] == "ALLOW_OR_PASS"]),
            "hold_review": hold_count,
            "block_risk": block_count,
        },
        "decision_totals": totals,
        "rows": rows,
        "portfolio_note": "QIRA, AgentSec, and DataCapsule currently pass their package-level local gates; these are local artifact signals only, not certification, readiness proof, or action authorization.",
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }


def dashboard_markdown(dashboard: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {product} | {package} | `{status}` | `{decision}` | {artifacts} |".format(
            product=row["product_name"],
            package=row["package"],
            status=row["status"],
            decision=row["primary_decision"],
            artifacts=row["artifact_count"],
        )
        for row in dashboard["rows"]
    )
    return f"""# ROE-2 Vertical Status Dashboard

Decision: `{dashboard['decision']}`

ROE-2 is a local read-only dashboard over existing QIRA, AgentSec, and DataCapsule artifacts.

| Vertical | Package | Status | Primary Decision | Artifacts |
| --- | --- | --- | --- | --- |
{rows}

## Portfolio Note

{dashboard['portfolio_note']}

## Boundary

This dashboard does not run probes, execute tools, enable workflows, call GitHub APIs, fetch URLs, upload packages, submit MCP Registry metadata, post to communities, request tokens, certify security, guarantee quality, prove product readiness, or authorize actions.
"""


def summary_markdown(dashboard: dict[str, Any]) -> str:
    counts = dashboard["status_counts"]
    return f"""# ROE-2 Summary

Decision: `{dashboard['decision']}`

- verticals: {dashboard['vertical_count']}
- allow/pass rows: {counts['allow_or_pass']}
- hold rows: {counts['hold_review']}
- block rows: {counts['block_risk']}

ROE-2 creates a shared artifact manifest and dashboard skeleton only. It is meant to help operate the parallel ResidualOps verticals without exposing private scoring kernels or implying certification.
"""


def next_steps_markdown(dashboard: dict[str, Any]) -> str:
    if dashboard["decision"] == "PASS_ROE2_DASHBOARD_READY":
        next_step = "DataCapsule-6 repository-owned corpus audit bundle or AgentSec-8 optional workflow artifact."
    else:
        next_step = "ROE-2 artifact remediation before adding more dashboard surfaces."
    return f"""# ROE-2 Next Steps

Recommended next step: {next_step}

The dashboard makes the portfolio easier to operate. The next product-building move should improve AgentSec because it is the strongest first external security vertical, while still reusing the shared ResidualOps artifact manifest.
"""


def run_vertical_status_dashboard(write_result: bool = True, root: Path | None = None) -> dict[str, Any]:
    dashboard = build_vertical_status_dashboard(root=root)
    if write_result:
        _write_json(DASHBOARD_JSON_PATH, dashboard, root=root)
        _write_text(DASHBOARD_MD_PATH, dashboard_markdown(dashboard), root=root)
        _write_text(SUMMARY_PATH, summary_markdown(dashboard), root=root)
        _write_text(NEXT_STEPS_PATH, next_steps_markdown(dashboard), root=root)
    return dashboard


def main() -> None:
    result = run_vertical_status_dashboard()
    print(f"residualops_dashboard: {result['decision']} verticals={result['vertical_count']}")


if __name__ == "__main__":
    main()
