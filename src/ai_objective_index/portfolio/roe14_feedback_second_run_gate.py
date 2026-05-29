from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_feedback_form import (
    AGENTSEC_PACKET_PATH,
    CLASSIFICATION_SAMPLE_PATH,
    DATACAPSULE_PACKET_PATH,
    FORM_TEMPLATE_PATH,
    KNOWN_LIMITS_PATH,
    MEMORY_UPDATE_SAMPLE_PATH,
    QIRA_PACKET_PATH,
    REDACTION_REPORT_PATH,
    REVIEWER_READOUT_PATH,
    SECOND_RUN_PLAN_SAMPLE_PATH,
    package_pilot_feedback,
)


OUTPUT_DIR = Path("public_launch") / "roe14"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE14_FEEDBACK_SECOND_RUN_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE14_FEEDBACK_SECOND_RUN_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE14_NEXT_ACTIONS.md"

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


def scan_feedback_claims(paths: list[Path]) -> list[dict[str, Any]]:
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
            previous = "\n".join(lines[max(0, line_number - 5) : line_number]).lower()
            if "what this is not" in previous or "claim boundary" in previous:
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": str(path).replace("\\", "/"), "line": line_number, "pattern": pattern.pattern})
                    break
    return findings


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-14 Feedback and Second-Run Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Feedback packets | `{result['feedback_packet_count']}` |
| Classifications | `{result['classification_count']}` |
| Second-run plans | `{result['second_run_plan_count']}` |
| Ready local plans | `{result['ready_local_second_run_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim findings | `{result['claim_finding_count']}` |
| Second run executed | `{result['second_run_executed']}` |

This is a local/offline feedback and second-run planning layer. It is not external action authorization, certification, proof, product readiness, or a quality guarantee.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-15 Local Owner-Consented Second-Run Receipt Packager" if result["decision"] == "PASS_PILOT_FEEDBACK_SECOND_RUN_READY" else "resolve ROE-14 HOLD/BLOCK findings"
    return f"""# ROE-14 Next Actions

Decision: `{result['decision']}`

Recommended next step: {next_step}.

Keep all feedback local and redacted. Do not call GitHub APIs, create issues, post comments, clone, fetch, crawl, run live MCP/tool calls, mutate repositories, merge, deploy, publish, upload, train, use credentials, or make certification/proof/product-readiness claims.
"""


def run_roe14_gate(write_result: bool = True, ensure_samples: bool = True) -> dict[str, Any]:
    generated = package_pilot_feedback(sample=True) if ensure_samples else {}
    classification_payload = generated.get("classifications") if generated else _read_json(CLASSIFICATION_SAMPLE_PATH).get("classifications", [])
    plan_payload = generated.get("second_run_plans") if generated else _read_json(SECOND_RUN_PLAN_SAMPLE_PATH).get("plans", [])
    memory_payload = generated.get("memory_updates") if generated else _read_json(MEMORY_UPDATE_SAMPLE_PATH).get("updates", [])
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    required = [
        FORM_TEMPLATE_PATH,
        AGENTSEC_PACKET_PATH,
        QIRA_PACKET_PATH,
        DATACAPSULE_PACKET_PATH,
        CLASSIFICATION_SAMPLE_PATH,
        SECOND_RUN_PLAN_SAMPLE_PATH,
        MEMORY_UPDATE_SAMPLE_PATH,
        REVIEWER_READOUT_PATH,
        REDACTION_REPORT_PATH,
        KNOWN_LIMITS_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    claim_findings = scan_feedback_claims(required + [Path("docs") / "portfolio" / "pilot_second_run_claim_boundaries.md"])
    classifications = classification_payload if isinstance(classification_payload, list) else []
    plans = plan_payload if isinstance(plan_payload, list) else []
    memory_updates = memory_payload if isinstance(memory_payload, list) else []
    second_run_executed = any(bool(plan.get("execute_now", False)) for plan in plans if isinstance(plan, dict))
    external_action = any(
        any(item in plan.get("allowed_operations", []) for item in ["github_api", "clone_repo", "fetch_url", "create_issue", "comment_on_pr", "merge", "deploy", "publish_package", "upload_data", "train_model"])
        for plan in plans
        if isinstance(plan, dict)
    )
    ready_count = len([plan for plan in plans if isinstance(plan, dict) and plan.get("run_status") == "READY_FOR_LOCAL_SECOND_RUN"])
    token_printed = bool(redaction.get("token_printed", False))
    private_kernel_exposed = bool(redaction.get("private_kernel_exposed", False))

    if missing:
        decision = "HOLD_MISSING_FEEDBACK_FORM" if str(FORM_TEMPLATE_PATH).replace("\\", "/") in missing else "HOLD_MISSING_SECOND_RUN_PLAN"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_findings:
        decision = "BLOCK_OVERCLAIM"
    elif external_action or second_run_executed:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif private_kernel_exposed:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    else:
        decision = "PASS_PILOT_FEEDBACK_SECOND_RUN_READY"

    result = {
        "schema": "ResidualOps_ROE14FeedbackSecondRunGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "feedback_packet_count": 3,
        "classification_count": len(classifications),
        "second_run_plan_count": len(plans),
        "feedback_memory_update_count": len(memory_updates),
        "ready_local_second_run_count": ready_count,
        "missing_artifacts": missing,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": redaction.get("finding_count", 0),
        "claim_finding_count": len(claim_findings),
        "claim_findings": claim_findings[:50],
        "second_run_executed": second_run_executed,
        "external_action_used": external_action,
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
    parser = argparse.ArgumentParser(description="Run the ROE-14 feedback and second-run gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-sample", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe14_gate(write_result=not args.no_write, ensure_samples=not args.no_sample)
    print(
        "roe14_feedback_second_run_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} ready={result['ready_local_second_run_count']}"
    )


if __name__ == "__main__":
    main()
