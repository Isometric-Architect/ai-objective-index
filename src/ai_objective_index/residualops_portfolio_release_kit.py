from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_artifact_manifest import MANIFEST_PATH, build_shared_artifact_manifest
from .residualops_dashboard import DASHBOARD_JSON_PATH, build_vertical_status_dashboard


OUTPUT_DIR = Path("public_launch") / "roe3"
PORTFOLIO_KIT_PATH = OUTPUT_DIR / "ROE3_PORTFOLIO_RELEASE_KIT.json"
RELEASE_NOTES_PATH = OUTPUT_DIR / "ROE3_PORTFOLIO_RELEASE_NOTES.md"
PUBLIC_VERTICAL_INDEX_PATH = OUTPUT_DIR / "ROE3_PUBLIC_VERTICAL_INDEX.md"
OPERATOR_HANDOFF_PATH = OUTPUT_DIR / "ROE3_OPERATOR_HANDOFF.md"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "ROE3_ARTIFACT_MANIFEST.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "ROE3_NEXT_STEPS.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _read_json(relative: Path) -> dict[str, Any]:
    path = _repo_root() / relative
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _sha256(relative: Path) -> str | None:
    path = _repo_root() / relative
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest() -> dict[str, Any]:
    manifest = _read_json(MANIFEST_PATH)
    if manifest:
        return manifest
    return build_shared_artifact_manifest()


def _load_dashboard() -> dict[str, Any]:
    dashboard = _read_json(DASHBOARD_JSON_PATH)
    if dashboard:
        return dashboard
    return build_vertical_status_dashboard()


def _vertical_summary(manifest: dict[str, Any], dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    dashboard_rows = {row.get("vertical_id"): row for row in dashboard.get("rows", [])}
    summaries: list[dict[str, Any]] = []
    for vertical in manifest.get("verticals", []):
        row = dashboard_rows.get(vertical.get("vertical_id"), {})
        summaries.append(
            {
                "vertical_id": vertical.get("vertical_id", "unknown"),
                "product_name": vertical.get("product_name", "unknown"),
                "package": vertical.get("package", "unknown"),
                "public_role": vertical.get("public_role", ""),
                "primary_decision": vertical.get("primary_decision", "unknown"),
                "status": row.get("status", "UNKNOWN"),
                "artifact_count": len(vertical.get("artifacts", [])),
                "missing_artifact_count": len([item for item in vertical.get("artifacts", []) if not item.get("exists")]),
                "primary_result": vertical.get("primary_result", ""),
                "claim_audit": vertical.get("claim_audit", ""),
                "safe_flags": vertical.get("safe_flags", {}),
                "known_limits": vertical.get("known_limits", []),
                "must_not_claim": vertical.get("must_not_claim", []),
            }
        )
    return summaries


def build_portfolio_release_kit(manifest: dict[str, Any] | None = None, dashboard: dict[str, Any] | None = None) -> dict[str, Any]:
    active_manifest = manifest or _load_manifest()
    active_dashboard = dashboard or _load_dashboard()
    verticals = _vertical_summary(active_manifest, active_dashboard)
    missing = []
    for vertical in verticals:
        if vertical["missing_artifact_count"]:
            missing.append(vertical["vertical_id"])
    decision = "PASS_ROE3_PORTFOLIO_RELEASE_KIT" if not missing else "HOLD_ROE3_VERTICAL_ARTIFACTS_MISSING"
    return {
        "schema": "ResidualOps_PortfolioReleaseKit/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "source_manifest": str(MANIFEST_PATH).replace("\\", "/"),
        "source_dashboard": str(DASHBOARD_JSON_PATH).replace("\\", "/"),
        "vertical_count": len(verticals),
        "verticals": verticals,
        "status_counts": active_dashboard.get("status_counts", {}),
        "decision_totals": active_dashboard.get("decision_totals", active_manifest.get("totals", {})),
        "release_surfaces": [
            str(RELEASE_NOTES_PATH).replace("\\", "/"),
            str(PUBLIC_VERTICAL_INDEX_PATH).replace("\\", "/"),
            str(OPERATOR_HANDOFF_PATH).replace("\\", "/"),
            str(ARTIFACT_MANIFEST_PATH).replace("\\", "/"),
        ],
        "known_limits": [
            "portfolio release kit only",
            "local artifact packaging only",
            "no workflow enablement",
            "no GitHub API call",
            "no PR comment posting",
            "no crawling",
            "no live MCP call",
            "no external tool execution",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not product-readiness proof",
            "not legal, privacy, license, or evaluation-cleanliness proof",
            "not action authorization",
        ],
        "must_not_claim": [
            "do not claim verified capability",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim legal sufficiency",
            "do not claim privacy compliance",
            "do not claim license clearance",
            "do not claim evaluation cleanliness",
            "do not claim external action authorization",
        ],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "github_api_used": False,
        "review_comment_posted": False,
        "crawler_used": False,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }


def release_notes_markdown(kit: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {name} | {package} | `{decision}` | {role} |".format(
            name=vertical["product_name"],
            package=vertical["package"],
            decision=vertical["primary_decision"],
            role=vertical["public_role"],
        )
        for vertical in kit["verticals"]
    )
    return f"""# ROE-3 Portfolio Release Notes

Decision: `{kit['decision']}`

ROE-3 packages the current QIRA, AgentSec, and DataCapsule local artifacts into one public-safe ResidualOps portfolio view.

| Vertical | Package | Primary Decision | Public Role |
| --- | --- | --- | --- |
{rows}

## What This Adds

- A unified release kit over QIRA-8, AgentSec-7, and DataCapsule-6.
- A public vertical index for comparing the current artifact surfaces.
- An operator handoff for the next productization steps.
- A release artifact manifest for the ROE-3 files themselves.

## Boundary

ROE-3 does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/eval status, or authorize actions.
"""


def public_vertical_index_markdown(kit: dict[str, Any]) -> str:
    sections = []
    for vertical in kit["verticals"]:
        limits = "\n".join(f"- {item}" for item in vertical.get("known_limits", [])[:8]) or "- Local artifact limits apply."
        sections.append(
            f"""## {vertical['product_name']}

- Package: `{vertical['package']}`
- Status: `{vertical['status']}`
- Primary decision: `{vertical['primary_decision']}`
- Public role: {vertical['public_role']}
- Primary result: `{vertical['primary_result']}`
- Claim audit: `{vertical['claim_audit']}`

Limits:

{limits}
"""
        )
    return "# ROE-3 Public Vertical Index\n\n" + "\n".join(sections)


def operator_handoff_markdown(kit: dict[str, Any]) -> str:
    return f"""# ROE-3 Operator Handoff

Decision: `{kit['decision']}`

This handoff is for operating the current public-safe ResidualOps portfolio without exposing private kernels or implying readiness claims.

## Current Stack

1. QIRA-Code ReleaseGate: local code/PR review artifact bundle.
2. AgentSec Gate: local MCP/tool manifest review artifact bundle.
3. DataCapsule / AIDREG Engine: local data-use metadata audit artifact bundle.

## Recommended Next Move

Build `AgentSec-8 optional workflow artifact` only as an opt-in workflow artifact, or start `ROE-4 private/public distribution split` if exposure increases.

## Operator Rules

- Keep exact weights, thresholds, provider priors, anti-gaming rules, private probe seeds, private negative controls, and commercial routing policy non-public.
- Do not post generated comments automatically.
- Do not run live MCP calls or external tools from these packages.
- Do not use these artifacts as verification, certification, legal/privacy/license proof, production-readiness proof, or action authorization.
"""


def build_artifact_manifest(output_paths: list[Path] | None = None) -> dict[str, Any]:
    selected = output_paths or [
        PORTFOLIO_KIT_PATH,
        RELEASE_NOTES_PATH,
        PUBLIC_VERTICAL_INDEX_PATH,
        OPERATOR_HANDOFF_PATH,
        NEXT_STEPS_PATH,
    ]
    records = []
    for relative in selected:
        path = _repo_root() / relative
        exists = path.exists() and path.is_file()
        records.append(
            {
                "path": str(relative).replace("\\", "/"),
                "exists": exists,
                "bytes": path.stat().st_size if exists else 0,
                "sha256": _sha256(relative) if exists else None,
            }
        )
    missing = [record["path"] for record in records if not record["exists"]]
    return {
        "schema": "ResidualOps_PortfolioArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_ROE3_ARTIFACT_MANIFEST" if not missing else "HOLD_ROE3_ARTIFACT_MISSING",
        "source_references": [
            {
                "path": str(MANIFEST_PATH).replace("\\", "/"),
                "exists": (_repo_root() / MANIFEST_PATH).exists(),
                "role": "ROE-2 shared artifact manifest input",
            },
            {
                "path": str(DASHBOARD_JSON_PATH).replace("\\", "/"),
                "exists": (_repo_root() / DASHBOARD_JSON_PATH).exists(),
                "role": "ROE-2 vertical status dashboard input",
            },
        ],
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }


def next_steps_markdown(kit: dict[str, Any]) -> str:
    return f"""# ROE-3 Next Steps

Decision: `{kit['decision']}`

1. Keep ROE-3 as a local portfolio release kit over existing artifacts.
2. Add AgentSec-8 optional workflow artifact only if repository-owner opt-in remains explicit.
3. Prepare ROE-4 public/private distribution split before increasing public exposure.
4. Continue keeping private scoring weights, thresholds, provider priors, anti-gaming policy details, private negative controls, private probe seeds, and commercial routing policy outside the public repo.
"""


def run_portfolio_release_kit(write_result: bool = True) -> dict[str, Any]:
    kit = build_portfolio_release_kit()
    if write_result:
        _write_json(PORTFOLIO_KIT_PATH, kit)
        _write_text(RELEASE_NOTES_PATH, release_notes_markdown(kit))
        _write_text(PUBLIC_VERTICAL_INDEX_PATH, public_vertical_index_markdown(kit))
        _write_text(OPERATOR_HANDOFF_PATH, operator_handoff_markdown(kit))
        _write_text(NEXT_STEPS_PATH, next_steps_markdown(kit))
        manifest = build_artifact_manifest()
        _write_json(ARTIFACT_MANIFEST_PATH, manifest)
    return kit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ROE-3 unified ResidualOps portfolio release kit.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_portfolio_release_kit(write_result=not args.no_write)
    print(f"residualops_portfolio_release_kit: {result['decision']} verticals={result['vertical_count']}")


if __name__ == "__main__":
    main()
