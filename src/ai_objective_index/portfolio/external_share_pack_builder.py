from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_pack_checksums import CHECKSUMS_PATH, build_share_checksums
from .external_share_pack_claim_audit import CLAIM_AUDIT_PATH, run_share_claim_audit
from .external_share_pack_distribution_gate import DISTRIBUTION_BOUNDARY_PATH, run_distribution_gate
from .external_share_pack_loader import load_external_share_sources
from .external_share_pack_manifest import MANIFEST_PATH, SHARE_DIR, build_share_manifest, timestamp
from .external_share_pack_operator_script import OPERATOR_SCRIPT_PATH, SCREENSHOT_SCRIPT_PATH, VIDEO_SCRIPT_PATH, write_operator_scripts
from .external_share_pack_redaction import REDACTION_REPORT_PATH, scan_share_pack_artifacts


README_PATH = SHARE_DIR / "README_EXTERNAL_SAFE_DEMO.md"
DEMO_HTML_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DEMO.html"
DEMO_MD_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DEMO.md"
DEMO_JSON_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DASHBOARD.json"
CLAIM_BOUNDARY_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_CLAIM_BOUNDARY.md"
KNOWN_LIMITS_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_KNOWN_LIMITS.md"
SHARE_DECISION_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_SHARE_DECISION.md"


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _strip_external_html(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>", "", html, flags=re.I | re.S)
    html = re.sub(r"<link\b[^>]*>", "", html, flags=re.I)
    html = re.sub(r"<form\b.*?</form>", "", html, flags=re.I | re.S)
    html = re.sub(r"https?://\S+", "#", html)
    return html


def _claim_banner_html() -> str:
    return (
        '<div class="banner"><strong>External-safe static demo.</strong> '
        "No network, no live connector, no external action, no certification, no product-readiness claim, and no private kernel exposure.</div>"
    )


def build_external_safe_html(source_html: str) -> str:
    cleaned = _strip_external_html(source_html)
    if "External-safe static demo" not in cleaned:
        cleaned = cleaned.replace("<body>", f"<body>\n  {_claim_banner_html()}", 1)
    cleaned = cleaned.replace("ResidualOps Pilot Dashboard", "ResidualOps External-Safe Demo")
    return cleaned


def build_readme() -> str:
    return """# ResidualOps External-Safe Demo Pack

This folder is a bounded static demo/share package generated from ROE-16 dashboard artifacts.

Use cases:

- internal review;
- investor or partner architecture walkthrough;
- controlled customer discovery with claim ceiling visible;
- bounded screenshot or non-live video with claim ceiling visible.

This is not a product launch, not an external pilot, not security certification, not code correctness proof, not legal/privacy/license/eval-clean proof, not product readiness, not a quality guarantee, and not external action authorization.

No live connector, network dispatch, credentials, raw private data, tokens, private kernels, deploy, publish, merge, upload, training, or external repository mutation is included.
"""


def build_claim_boundary() -> str:
    return """# ResidualOps External-Safe Claim Boundary

This share pack is a static local demo artifact.

It is not:

- no external pilot;
- no product launch;
- no security certification;
- no code correctness proof;
- no legal opinion;
- no privacy audit;
- no license clearance;
- no eval-clean proof;
- no quality guarantee;
- no product-readiness claim;
- no external action authorization.
"""


def build_known_limits() -> str:
    return """# ResidualOps External-Safe Known Limits

- Static/local/offline demo artifacts only.
- No live connector, no network calls, no GitHub API calls, no URL fetching, no crawling, no live MCP/tool calls.
- No raw private-data inspection, no upload, no training, no deploy, no publish, no posting, no merge, no external repository mutation.
- No credentials, tokens, private keys, private kernels, exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, or commercial routing policy.
- Not certification, proof, legal/privacy/license/eval-clean clearance, quality guarantee, product readiness, or action authorization.
"""


def build_share_decision(distribution: dict[str, Any]) -> str:
    return f"""# ResidualOps External-Safe Share Decision

Distribution decision: `{distribution['decision']}`

Requested mode: `{distribution['requested_distribution_mode']}`

Allowed current use: local static demo ZIP, internal review, bounded architecture walkthrough, and controlled customer discovery only when the claim ceiling is visible.

Review required before public blog, website teaser, broad recording distribution, partner security questionnaire use, or sandbox connector lab planning.

Blocked: production deployment, live connector demo, external action demo, public auto-posting, live credential use, network dispatch, token/raw PII export, security certification claim, legal/privacy compliance claim, product-ready badge, or mutable/rehosted claim surface.
"""


def _source_map() -> dict[str, str]:
    return {
        str(DEMO_HTML_PATH).replace("\\", "/"): "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.html",
        str(DEMO_MD_PATH).replace("\\", "/"): "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.md",
        str(DEMO_JSON_PATH).replace("\\", "/"): "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.json",
        str(CLAIM_BOUNDARY_PATH).replace("\\", "/"): "pilot_dashboard/RESIDUALOPS_PILOT_CLAIM_BOUNDARY.md",
    }


def share_artifact_paths(include_reports: bool = True) -> list[Path]:
    paths = [
        README_PATH,
        DEMO_HTML_PATH,
        DEMO_MD_PATH,
        DEMO_JSON_PATH,
        CLAIM_BOUNDARY_PATH,
        KNOWN_LIMITS_PATH,
        OPERATOR_SCRIPT_PATH,
        SCREENSHOT_SCRIPT_PATH,
        VIDEO_SCRIPT_PATH,
        SHARE_DECISION_PATH,
    ]
    if include_reports:
        paths.extend([MANIFEST_PATH, CHECKSUMS_PATH, REDACTION_REPORT_PATH, CLAIM_AUDIT_PATH, DISTRIBUTION_BOUNDARY_PATH])
    return paths


def build_share_pack_payload(source: dict[str, Any], manifest: dict[str, Any], distribution: dict[str, Any]) -> dict[str, Any]:
    dashboard = source["dashboard"]
    return {
        "schema": "ResidualOps_ExternalSafeSharePack/v0.1",
        "pack_id": "residualops-external-safe-demo-pack-v0-1",
        "generated_at": timestamp(),
        "mode": "static_local_redacted_demo",
        "source_dashboard_ref": "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.json",
        "included_artifacts": manifest.get("artifacts", []),
        "dashboard_summary": {
            "dashboard_id": dashboard.get("dashboard_id", ""),
            "vertical_count": len(dashboard.get("vertical_status_cards", [])),
            "second_run_allow": dashboard.get("aggregate_counts", {}).get("second_run_allow", 0),
            "second_run_hold": dashboard.get("aggregate_counts", {}).get("second_run_hold", 0),
            "second_run_block": dashboard.get("aggregate_counts", {}).get("second_run_block", 0),
            "external_action_count": dashboard.get("aggregate_counts", {}).get("external_action_count", 0),
        },
        "distribution_boundary": distribution,
        "hard_invariants": distribution.get("hard_invariants", {}),
        "claim_boundary": {
            "not_external_pilot": True,
            "not_product_launch": True,
            "not_security_certification": True,
            "not_code_correctness_proof": True,
            "not_legal_opinion": True,
            "not_privacy_audit": True,
            "not_license_clearance": True,
            "not_eval_clean_proof": True,
            "not_quality_guarantee": True,
            "not_product_ready": True,
            "no_external_action_authorization": True,
        },
        "known_limits": build_known_limits().splitlines()[2:],
        "recommended_next_action": "ROE-18 Pilot Discovery / Feedback Intake Outreach Drafts",
        "network_used": False,
        "external_actions_performed": False,
        "token_printed": False,
        "private_kernel_exposed": False,
    }


def generate_external_share_pack(write_result: bool = True) -> dict[str, Any]:
    source = load_external_share_sources()
    if source["decision"] != "PASS_SOURCE_DASHBOARD_LOADED":
        return {"source": source, "decision": "HOLD_MISSING_SOURCE_DASHBOARD"}
    if write_result:
        _write_text(README_PATH, build_readme())
        _write_text(DEMO_HTML_PATH, build_external_safe_html(source["dashboard_html"]))
        _write_text(DEMO_MD_PATH, "# ResidualOps External-Safe Demo\n\n" + source["dashboard_markdown"])
        _write_json(DEMO_JSON_PATH, source["dashboard"])
        _write_text(CLAIM_BOUNDARY_PATH, build_claim_boundary())
        _write_text(KNOWN_LIMITS_PATH, build_known_limits())
        write_operator_scripts()
        manifest = build_share_manifest(share_artifact_paths(include_reports=False), source_map=_source_map(), write_result=True)
        checksums = build_share_checksums(share_artifact_paths(include_reports=False) + [MANIFEST_PATH], write_result=True)
        redaction = scan_share_pack_artifacts(share_artifact_paths(include_reports=True), write_result=True)
        claim_audit = run_share_claim_audit(share_artifact_paths(include_reports=True), write_result=True)
        distribution = run_distribution_gate("local_static_demo_zip", write_result=True)
        _write_text(SHARE_DECISION_PATH, build_share_decision(distribution))
        manifest = build_share_manifest(share_artifact_paths(include_reports=True), source_map=_source_map(), write_result=True)
        checksums = build_share_checksums(share_artifact_paths(include_reports=True), write_result=True)
        redaction = scan_share_pack_artifacts(share_artifact_paths(include_reports=True), write_result=True)
        claim_audit = run_share_claim_audit(share_artifact_paths(include_reports=True), write_result=True)
        distribution = run_distribution_gate("local_static_demo_zip", write_result=True)
        _write_json(DEMO_JSON_PATH, build_share_pack_payload(source, manifest, distribution))
        manifest = build_share_manifest(share_artifact_paths(include_reports=True), source_map=_source_map(), write_result=True)
        checksums = build_share_checksums(share_artifact_paths(include_reports=True), write_result=True)
        redaction = scan_share_pack_artifacts(share_artifact_paths(include_reports=True), write_result=True)
        claim_audit = run_share_claim_audit(share_artifact_paths(include_reports=True), write_result=True)
        distribution = run_distribution_gate("local_static_demo_zip", write_result=True)
    else:
        manifest = {"artifact_count": 0, "artifacts": []}
        checksums = {"checksum_count": 0}
        redaction = {"decision": "NOT_WRITTEN"}
        claim_audit = {"decision": "NOT_WRITTEN"}
        distribution = {"decision": "NOT_WRITTEN"}
    return {
        "source": source,
        "manifest": manifest,
        "checksums": checksums,
        "redaction": redaction,
        "claim_audit": claim_audit,
        "distribution": distribution,
        "share_pack": _read_json(DEMO_JSON_PATH) if write_result else {},
    }


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the ROE-17 external-safe static demo/share pack.")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = generate_external_share_pack(write_result=not args.no_write)
    print(
        "external_share_pack_builder: "
        f"artifacts={result.get('manifest', {}).get('artifact_count', 0)} "
        f"redaction={result.get('redaction', {}).get('decision', 'UNKNOWN')} "
        f"claim_audit={result.get('claim_audit', {}).get('decision', 'UNKNOWN')} "
        f"distribution={result.get('distribution', {}).get('decision', 'UNKNOWN')}"
    )


if __name__ == "__main__":
    main()
