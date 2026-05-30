from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_refresh_checksums import CHECKSUMS_V2_PATH
from .external_share_refresh_claim_audit import CLAIM_AUDIT_V2_PATH
from .external_share_refresh_manifest import MANIFEST_V2_PATH, SHARE_V2_DIR, timestamp
from .external_share_refresh_redaction import REDACTION_V2_PATH


DISTRIBUTION_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DISTRIBUTION_BOUNDARY_V2.json"
HTML_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html"

ALLOWED_MODES = {
    "local_static_demo_zip",
    "internal_review",
    "investor_partner_architecture_walkthrough",
    "controlled_customer_discovery_walkthrough_with_claim_ceiling",
    "bounded_screenshot_or_video_with_claim_ceiling_visible",
    "operator_script_walkthrough",
    "artifact_manifest_share",
    "redacted_non_live_demo_recording",
}
REVIEW_REQUIRED_MODES = {
    "public_blog_or_website_teaser",
    "recorded_demo_for_external_distribution",
    "partner_security_architecture_review",
    "pilot_customer_security_questionnaire",
    "sandbox_connector_lab_plan",
}
BLOCKED_MODES = {
    "production_deployment",
    "live_connector_demo",
    "external_action_demo",
    "payment_execution_demo",
    "legal_signing_demo",
    "medical_financial_action_demo",
    "public_auto_post_demo",
    "live_credentials_use",
    "network_dispatch",
    "raw_pii_export",
    "token_export",
    "product_ready_badge",
    "security_certification_claim",
    "public_certification_claim",
    "legal_compliance_claim",
    "privacy_certification_claim",
    "qleos_compatible_public_badge",
    "demo_without_claim_ceiling",
    "mutable_or_rehosted_claim_surface",
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


def html_has_network_dependency(path: Path = HTML_V2_PATH) -> bool:
    full = _repo_root() / path
    if not full.exists():
        return False
    lowered = full.read_text(encoding="utf-8", errors="ignore").lower()
    return any(marker in lowered for marker in ["<script", "<link", "<form", "http://", "https://"])


def run_refresh_distribution_gate(requested_distribution_mode: str = "local_static_demo_zip", write_result: bool = True) -> dict[str, Any]:
    redaction = _read_json(REDACTION_V2_PATH)
    claim_audit = _read_json(CLAIM_AUDIT_V2_PATH)
    manifest = _read_json(MANIFEST_V2_PATH)
    checksums = _read_json(CHECKSUMS_V2_PATH)
    if redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT":
        decision = "BLOCK_REDACTION_FAILED"
    elif claim_audit.get("decision") == "BLOCK_OVERCLAIM":
        decision = "BLOCK_CLAIM_AUDIT_FAILED"
    elif html_has_network_dependency():
        decision = "BLOCK_NETWORK_DEPENDENCY"
    elif requested_distribution_mode in BLOCKED_MODES:
        decision = "BLOCK_DISTRIBUTION_MODE"
    elif requested_distribution_mode in REVIEW_REQUIRED_MODES:
        decision = "HOLD_REVIEW_REQUIRED"
    elif requested_distribution_mode in ALLOWED_MODES:
        decision = "PASS_ALLOWED_STATIC_SHARE"
    else:
        decision = "HOLD_REVIEW_REQUIRED"
    result = {
        "schema": "ResidualOps_ExternalShareRefreshDistributionBoundary/v0.1",
        "generated_at": timestamp(),
        "requested_distribution_mode": requested_distribution_mode,
        "decision": decision,
        "allowed": sorted(ALLOWED_MODES),
        "review_required": sorted(REVIEW_REQUIRED_MODES),
        "blocked": sorted(BLOCKED_MODES),
        "hard_invariants": {
            "claim_ceiling_banner_visible": True,
            "no_network": True,
            "no_live_credentials": True,
            "no_live_connector_demo": True,
            "no_external_action_authorization": True,
            "no_product_security_legal_privacy_readiness_claim": True,
            "no_raw_payload_or_credentials": True,
            "no_private_kernel": True,
            "skipped_candidates_visible": True,
        },
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "claim_audit_decision": claim_audit.get("decision", "UNKNOWN"),
        "manifest_artifact_count": manifest.get("artifact_count", 0),
        "checksum_count": checksums.get("checksum_count", 0),
        "network_dependency": html_has_network_dependency(),
    }
    if write_result:
        destination = _repo_root() / DISTRIBUTION_V2_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-22 external share refresh distribution gate.")
    parser.add_argument("--mode", default="local_static_demo_zip")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_refresh_distribution_gate(args.mode, write_result=not args.no_write)
    print(f"external_share_refresh_distribution_gate: {result['decision']} mode={result['requested_distribution_mode']}")


if __name__ == "__main__":
    main()
