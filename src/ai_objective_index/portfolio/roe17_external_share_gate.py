from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_pack_builder import (
    CLAIM_BOUNDARY_PATH,
    DEMO_HTML_PATH,
    DEMO_JSON_PATH,
    DEMO_MD_PATH,
    KNOWN_LIMITS_PATH,
    README_PATH,
    SHARE_DECISION_PATH,
    generate_external_share_pack,
)
from .external_share_pack_checksums import CHECKSUMS_PATH
from .external_share_pack_claim_audit import CLAIM_AUDIT_PATH
from .external_share_pack_distribution_gate import DISTRIBUTION_BOUNDARY_PATH
from .external_share_pack_manifest import MANIFEST_PATH
from .external_share_pack_redaction import REDACTION_REPORT_PATH


OUTPUT_DIR = Path("public_launch") / "roe17"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE17_EXTERNAL_SHARE_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE17_EXTERNAL_SHARE_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE17_NEXT_ACTIONS.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def html_has_network_dependency(path: Path = DEMO_HTML_PATH) -> bool:
    full = _repo_root() / path
    if not full.exists():
        return False
    text = full.read_text(encoding="utf-8", errors="ignore")
    return bool(re.search(r"<script\b|<link\b|<form\b|https?://", text, re.I))


def claim_ceiling_visible() -> bool:
    full = _repo_root() / DEMO_HTML_PATH
    if not full.exists():
        return False
    text = full.read_text(encoding="utf-8", errors="ignore").lower()
    return "external-safe static demo" in text and "not certification" in text


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-17 External Share Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Pack ID | `{result['pack_id']}` |
| Artifacts | `{result['artifact_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim audit | `{result['claim_audit_decision']}` |
| Distribution | `{result['distribution_decision']}` |
| Network dependency | `{result['network_dependency']}` |
| Claim ceiling visible | `{result['claim_ceiling_visible']}` |

ROE-17 is a bounded static/local share pack. It is not a product launch, certification, proof, product-readiness claim, quality guarantee, or external action authorization.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-18 Pilot Discovery / Feedback Intake Outreach Drafts" if result["decision"] == "PASS_EXTERNAL_SAFE_DEMO_SHARE_PACK_READY" else "resolve ROE-17 HOLD/BLOCK findings"
    return f"""# ROE-17 Next Actions

Decision: `{result['decision']}`

Recommended next package: {next_step}.

Use the share pack only for bounded review with the claim ceiling visible. Do not deploy, post publicly, run live connectors, use credentials, expose private kernels, or make certification/product-readiness/action-authorization claims.
"""


def run_roe17_gate(write_result: bool = True, ensure_share_pack: bool = True) -> dict[str, Any]:
    generated = generate_external_share_pack(write_result=True) if ensure_share_pack else {}
    share_pack = generated.get("share_pack") if generated else _read_json(DEMO_JSON_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    claim_audit = generated.get("claim_audit") if generated else _read_json(CLAIM_AUDIT_PATH)
    distribution = generated.get("distribution") if generated else _read_json(DISTRIBUTION_BOUNDARY_PATH)
    manifest = generated.get("manifest") if generated else _read_json(MANIFEST_PATH)
    required = [
        README_PATH,
        DEMO_HTML_PATH,
        DEMO_MD_PATH,
        DEMO_JSON_PATH,
        CLAIM_BOUNDARY_PATH,
        KNOWN_LIMITS_PATH,
        MANIFEST_PATH,
        CHECKSUMS_PATH,
        REDACTION_REPORT_PATH,
        CLAIM_AUDIT_PATH,
        DISTRIBUTION_BOUNDARY_PATH,
        SHARE_DECISION_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not (_repo_root() / path).exists()]
    network_dependency = html_has_network_dependency()
    ceiling_visible = claim_ceiling_visible()
    distribution_decision = distribution.get("decision", "UNKNOWN")
    token_printed = bool(redaction.get("token_printed", False) or share_pack.get("token_printed", False))
    private_kernel = bool(redaction.get("private_kernel_exposed", False) or share_pack.get("private_kernel_exposed", False))
    if missing:
        decision = "HOLD_MISSING_ARTIFACT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif claim_audit.get("decision") == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
    elif network_dependency:
        decision = "BLOCK_NETWORK_DEPENDENCY"
    elif private_kernel:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif distribution_decision == "HOLD_REVIEW_REQUIRED":
        decision = "HOLD_REVIEW_REQUIRED"
    elif distribution_decision != "PASS_ALLOWED_STATIC_SHARE":
        decision = "BLOCK_UNSAFE_DISTRIBUTION_MODE"
    elif not ceiling_visible:
        decision = "HOLD_REVIEW_REQUIRED"
    else:
        decision = "PASS_EXTERNAL_SAFE_DEMO_SHARE_PACK_READY"
    result = {
        "schema": "ResidualOps_ROE17ExternalShareGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "pack_id": share_pack.get("pack_id", ""),
        "artifact_count": int(manifest.get("artifact_count", 0) or 0),
        "missing_artifacts": missing,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": int(redaction.get("finding_count", 0) or 0),
        "claim_audit_decision": claim_audit.get("decision", "UNKNOWN"),
        "claim_audit_findings": int(claim_audit.get("risky_phrase_count", 0) or 0),
        "distribution_decision": distribution_decision,
        "requested_distribution_mode": distribution.get("requested_distribution_mode", ""),
        "network_dependency": network_dependency,
        "claim_ceiling_visible": ceiling_visible,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel,
        "raw_private_data_included": False,
        "external_actions_performed": False,
        "can_certify_security": False,
        "can_prove_code_correctness": False,
        "can_provide_legal_privacy_license_eval_proof": False,
        "can_claim_product_readiness": False,
        "can_authorize_external_action": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, _summary_markdown(result))
        _write_text(NEXT_ACTIONS_PATH, _next_actions_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-17 external-safe share pack gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-share-pack", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe17_gate(write_result=not args.no_write, ensure_share_pack=not args.no_share_pack)
    print(
        "roe17_external_share_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} "
        f"claim_audit={result['claim_audit_decision']} distribution={result['distribution_decision']}"
    )


if __name__ == "__main__":
    main()
