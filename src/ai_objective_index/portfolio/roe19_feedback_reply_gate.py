from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .feedback_reply_intake import (
    CLASSIFICATION_SAMPLE_PATH,
    KNOWN_LIMITS_PATH,
    MEMORY_CANDIDATE_SAMPLE_PATH,
    READOUT_PATH,
    REDACTION_REPORT_PATH,
    ROUTE_SAMPLE_PATH,
    SECOND_RUN_CANDIDATE_SAMPLE_PATH,
    TRIAGE_SAMPLE_PATH,
    package_feedback_replies,
)
from .feedback_reply_packet import sample_packet_paths, sample_reply_paths


OUTPUT_DIR = Path("public_launch") / "roe19"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE19_FEEDBACK_REPLY_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE19_FEEDBACK_REPLY_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE19_NEXT_ACTIONS.md"


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _required_artifacts() -> list[Path]:
    return [
        *sample_reply_paths().values(),
        *sample_packet_paths().values(),
        CLASSIFICATION_SAMPLE_PATH,
        ROUTE_SAMPLE_PATH,
        TRIAGE_SAMPLE_PATH,
        MEMORY_CANDIDATE_SAMPLE_PATH,
        SECOND_RUN_CANDIDATE_SAMPLE_PATH,
        REDACTION_REPORT_PATH,
        READOUT_PATH,
        KNOWN_LIMITS_PATH,
    ]


def _summary(result: dict[str, Any]) -> str:
    return f"""# ROE-19 Feedback Reply Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Reply packets | `{result['reply_packet_count']}` |
| Classifications | `{result['classification_count']}` |
| Routes | `{result['route_count']}` |
| Triage entries | `{result['triage_count']}` |
| Memory candidates | `{result['memory_candidate_count']}` |
| Second-run candidates | `{result['second_run_candidate_count']}` |
| Redaction | `{result['redaction_decision']}` |

ROE-19 converts local/offline feedback replies into packets, classifications, routes, triage entries, memory candidates, and second-run candidates without sending, posting, API calls, or external actions.
"""


def _next_actions(result: dict[str, Any]) -> str:
    next_step = "ROE-20 Local Feedback-to-Second-Run Execution Bridge" if result["decision"] == "PASS_FEEDBACK_REPLY_PACKET_INTAKE_READY" else "resolve ROE-19 HOLD/BLOCK findings"
    return f"""# ROE-19 Next Actions

Decision: `{result['decision']}`

Recommended next package: {next_step}.

Continue only with local, redacted, owner-consented artifacts. Do not send replies, create GitHub issues, post comments, call APIs, fetch URLs, upload, train, merge, deploy, publish, or claim certification/product readiness.
"""


def run_roe19_gate(write_result: bool = True, ensure_pack: bool = True) -> dict[str, Any]:
    generated = package_feedback_replies(sample=True) if ensure_pack else {}
    classifications = generated.get("classifications") if generated else _read_json(CLASSIFICATION_SAMPLE_PATH).get("classifications", [])
    routes = generated.get("routes") if generated else _read_json(ROUTE_SAMPLE_PATH).get("routes", [])
    triage = generated.get("triage") if generated else _read_json(TRIAGE_SAMPLE_PATH).get("triage", [])
    memory = generated.get("memory_candidates") if generated else _read_json(MEMORY_CANDIDATE_SAMPLE_PATH).get("candidates", [])
    second_run = generated.get("second_run_candidates") if generated else _read_json(SECOND_RUN_CANDIDATE_SAMPLE_PATH).get("candidates", [])
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    missing = [str(path).replace("\\", "/") for path in _required_artifacts() if not (_repo_root() / path).exists()]
    block_classifications = [item.get("classification", "") for item in classifications if str(item.get("classification", "")).startswith("BLOCK_")]
    auto_send = False
    external_api = False
    external_action = bool(block_classifications and any("EXTERNAL_ACTION" in item for item in block_classifications))
    overclaim = bool(block_classifications and any("CERTIFICATION" in item or "READINESS" in item for item in block_classifications))
    private_kernel = bool(redaction.get("private_kernel_exposed", False) or any("PRIVATE_KERNEL" in item for item in block_classifications))
    token_secret = bool(redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or any("SECRET" in item for item in block_classifications))

    if missing and any("PACKET" in item for item in missing):
        decision = "HOLD_MISSING_REPLY_PACKET"
    elif missing and any("CLASSIFICATION" in item for item in missing):
        decision = "HOLD_MISSING_CLASSIFICATION"
    elif missing:
        decision = "HOLD_MISSING_REPLY_PACKET"
    elif token_secret:
        decision = "BLOCK_SECRET_FINDING"
    elif overclaim:
        decision = "BLOCK_OVERCLAIM"
    elif external_action:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif auto_send:
        decision = "BLOCK_AUTO_SEND"
    elif private_kernel:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif redaction.get("decision") != "PASS_REDACTED":
        decision = "HOLD_REDACTION_REVIEW"
    else:
        decision = "PASS_FEEDBACK_REPLY_PACKET_INTAKE_READY"

    result = {
        "schema": "ResidualOps_ROE19FeedbackReplyGate/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "reply_packet_count": len(generated.get("packets", [])) if generated else len(sample_packet_paths()),
        "classification_count": len(classifications),
        "route_count": len(routes),
        "triage_count": len(triage),
        "memory_candidate_count": len(memory),
        "second_run_candidate_count": len(second_run),
        "missing_artifacts": missing,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": int(redaction.get("finding_count", 0) or 0),
        "auto_send_performed": auto_send,
        "external_api_used": external_api,
        "external_actions_performed": False,
        "token_printed": False,
        "private_kernel_exposed": private_kernel,
        "can_send_reply": False,
        "can_create_github_issue": False,
        "can_certify_security": False,
        "can_claim_product_readiness": False,
        "can_authorize_external_action": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, _summary(result))
        _write_text(NEXT_ACTIONS_PATH, _next_actions(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-19 feedback reply packet intake gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-generate", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe19_gate(write_result=not args.no_write, ensure_pack=not args.no_generate)
    print(
        "roe19_feedback_reply_gate: "
        f"{result['decision']} packets={result['reply_packet_count']} routes={result['route_count']} "
        f"redaction={result['redaction_decision']} auto_send={result['auto_send_performed']} "
        f"external_api={result['external_api_used']}"
    )


if __name__ == "__main__":
    main()
