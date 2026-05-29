from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .second_run_artifact_index import ARTIFACT_INDEX_PATH
from .second_run_executor import (
    AGENTSEC_DELTA_PATH,
    AGENTSEC_RESULT_PATH,
    DATACAPSULE_DELTA_PATH,
    DATACAPSULE_RESULT_PATH,
    FEEDBACK_MEMORY_PATH,
    KNOWN_LIMITS_PATH,
    QIRA_DELTA_PATH,
    QIRA_RESULT_PATH,
    RECEIPT_PATH,
    REVIEWER_READOUT_PATH,
    run_second_run,
)
from .second_run_redaction import REDACTION_REPORT_PATH


OUTPUT_DIR = Path("public_launch") / "roe15"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE15_SECOND_RUN_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE15_SECOND_RUN_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE15_NEXT_ACTIONS.md"

RISKY_PATTERNS = [
    re.compile(r"\bsecurity\s+certification\b", re.I),
    re.compile(r"\bcode\s+correctness\s+proof\b", re.I),
    re.compile(r"\blegal\s+clearance\b", re.I),
    re.compile(r"\bprivacy\s+clearance\b", re.I),
    re.compile(r"\blicense\s+clearance\b", re.I),
    re.compile(r"\beval[-\s]+clean\s+proof\b", re.I),
    re.compile(r"\bquality\s+guarantee\b", re.I),
    re.compile(r"\bproduct\s+readiness\b", re.I),
    re.compile(r"\bexternal\s+action\s+authorization\b", re.I),
]
SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "cannot ", "without ", "must not", "claim boundary", "must_not_claim", "known limits"]


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


def _exists(path: Path) -> bool:
    return (_repo_root() / path).exists()


def scan_second_run_claims(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if not full.exists() or not full.is_file():
            continue
        lines = full.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            if any(marker in lowered for marker in SAFE_CONTEXT):
                continue
            previous = "\n".join(lines[max(0, line_number - 12) : line_number]).lower()
            if "what this is not" in previous or "claim boundary" in previous or "must_not_claim" in previous:
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": str(path).replace("\\", "/"), "line": line_number, "pattern": pattern.pattern})
                    break
    return findings


def _unsafe_upgrade(deltas: list[dict[str, Any]]) -> bool:
    for delta in deltas:
        changes = delta.get("decision_changes", {})
        if int(changes.get("block_to_allow_count", 0) or 0) > 0:
            return True
        if int(changes.get("hold_to_allow_count", 0) or 0) > 0:
            return True
        if delta.get("unsafe_decision_upgrade_detected"):
            return True
        if delta.get("certification_upgrade_detected"):
            return True
        if delta.get("external_action_authorized"):
            return True
    return False


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-15 Second-Run Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Verticals | `{result['vertical_count']}` |
| Prior ALLOW/HOLD/BLOCK | `{result['prior_allow_count']}/{result['prior_hold_count']}/{result['prior_block_count']}` |
| New ALLOW/HOLD/BLOCK | `{result['new_allow_count']}/{result['new_hold_count']}/{result['new_block_count']}` |
| Finding updates | `{result['finding_updates_count']}` |
| Fixture candidates | `{result['fixture_candidate_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim findings | `{result['claim_finding_count']}` |
| Unsafe upgrade | `{result['unsafe_decision_upgrade_detected']}` |

ROE-15 is a local/sample second-run receipt update. It is not an external pilot, certification, proof, product readiness, quality guarantee, or action authorization.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-16 Pilot Dashboard Artifact Pack" if result["decision"] == "PASS_LOCAL_SECOND_RUN_RECEIPT_READY" else "resolve ROE-15 HOLD/BLOCK findings"
    return f"""# ROE-15 Next Actions

Decision: `{result['decision']}`

Recommended next step: {next_step}.

Keep all second-run work local and redacted. Do not call GitHub APIs, create issues or comments, clone, fetch, crawl, run live MCP/tool calls, mutate repositories, merge, deploy, publish, upload, train, use credentials, or make certification/proof/product-readiness claims.
"""


def run_roe15_gate(write_result: bool = True, ensure_second_run: bool = True) -> dict[str, Any]:
    generated = run_second_run(sample=True, write_result=True) if ensure_second_run else {}
    receipt = generated.get("receipt") if generated else _read_json(RECEIPT_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    artifact_index = generated.get("artifact_index") if generated else _read_json(ARTIFACT_INDEX_PATH)
    required = [
        RECEIPT_PATH,
        AGENTSEC_RESULT_PATH,
        QIRA_RESULT_PATH,
        DATACAPSULE_RESULT_PATH,
        AGENTSEC_DELTA_PATH,
        QIRA_DELTA_PATH,
        DATACAPSULE_DELTA_PATH,
        FEEDBACK_MEMORY_PATH,
        REVIEWER_READOUT_PATH,
        REDACTION_REPORT_PATH,
        ARTIFACT_INDEX_PATH,
        KNOWN_LIMITS_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    claim_findings = scan_second_run_claims(required + [Path("docs") / "portfolio" / "second_run_claim_boundaries.md"])
    summary = receipt.get("aggregate_summary", {}) if isinstance(receipt, dict) else {}
    deltas = receipt.get("deltas", []) if isinstance(receipt, dict) else []
    external_action = bool(
        summary.get("external_action_count", 0)
        or receipt.get("external_actions_performed", False)
        or receipt.get("github_api_used", False)
        or receipt.get("live_mcp_call_used", False)
        or receipt.get("merge_deploy_publish_performed", False)
        or receipt.get("upload_or_training_performed", False)
    )
    unsafe_upgrade = _unsafe_upgrade(deltas)
    token_printed = bool(redaction.get("token_printed", False) or receipt.get("token_printed", False))
    private_kernel_exposed = bool(redaction.get("private_kernel_exposed", False) or receipt.get("private_kernel_exposed", False))

    if missing:
        delta_missing = any("DELTA" in item for item in missing)
        decision = "HOLD_MISSING_DELTA" if delta_missing else "HOLD_MISSING_READOUT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_findings:
        decision = "BLOCK_OVERCLAIM"
    elif external_action:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif unsafe_upgrade:
        decision = "BLOCK_UNSAFE_DECISION_UPGRADE"
    elif private_kernel_exposed:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    else:
        decision = "PASS_LOCAL_SECOND_RUN_RECEIPT_READY"

    result = {
        "schema": "ResidualOps_ROE15SecondRunGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "second_run_id": receipt.get("second_run_id", ""),
        "vertical_count": int(summary.get("vertical_count", 0) or 0),
        "prior_allow_count": int(summary.get("prior_allow_count", 0) or 0),
        "prior_hold_count": int(summary.get("prior_hold_count", 0) or 0),
        "prior_block_count": int(summary.get("prior_block_count", 0) or 0),
        "new_allow_count": int(summary.get("new_allow_count", 0) or 0),
        "new_hold_count": int(summary.get("new_hold_count", 0) or 0),
        "new_block_count": int(summary.get("new_block_count", 0) or 0),
        "finding_updates_count": int(summary.get("finding_updates_count", 0) or 0),
        "fixture_candidate_count": int(summary.get("fixture_candidate_count", 0) or 0),
        "negative_control_candidate_count": int(summary.get("negative_control_candidate_count", 0) or 0),
        "claim_boundary_change_count": int(summary.get("claim_boundary_change_count", 0) or 0),
        "missing_artifacts": missing,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": redaction.get("finding_count", 0),
        "artifact_count": artifact_index.get("artifact_count", 0),
        "claim_finding_count": len(claim_findings),
        "claim_findings": claim_findings[:50],
        "external_action_used": external_action,
        "unsafe_decision_upgrade_detected": unsafe_upgrade,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel_exposed,
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
    parser = argparse.ArgumentParser(description="Run the ROE-15 local second-run receipt gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-second-run", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe15_gate(write_result=not args.no_write, ensure_second_run=not args.no_second_run)
    print(
        "roe15_second_run_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} "
        f"new={result['new_allow_count']}/{result['new_hold_count']}/{result['new_block_count']}"
    )


if __name__ == "__main__":
    main()
