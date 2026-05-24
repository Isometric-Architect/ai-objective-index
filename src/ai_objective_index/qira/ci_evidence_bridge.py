from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .ci_evidence import CiCheckResult, CiEvidencePacket, build_qira6_ci_review, validate_ci_evidence
from .packet_generator import generate_packet_from_request, sample_generation_request
from .packet_loader import load_task_packet


BridgeDecision = Literal[
    "PASS_QIRA7_CI_EVIDENCE_BRIDGE",
    "HOLD_QIRA7_PACKET_REQUIRED",
    "HOLD_QIRA7_CI_EVIDENCE_PARTIAL",
    "BLOCK_QIRA7_CI_EVIDENCE",
]

OUTPUT_DIR = Path("public_launch") / "qira7"
SAMPLE_PACKET_PATH = OUTPUT_DIR / "QIRA7_SAMPLE_TASK_PACKET.json"
BRIDGE_EVIDENCE_PATH = OUTPUT_DIR / "QIRA7_CI_EVIDENCE.json"
VALIDATION_RESULT_PATH = OUTPUT_DIR / "QIRA7_VALIDATION_RESULT.json"
AUGMENTED_PACKET_PATH = OUTPUT_DIR / "QIRA7_AUGMENTED_TASK_PACKET.json"
REVIEW_RESULT_PATH = OUTPUT_DIR / "QIRA7_REVIEW_RESULT.json"
BRIDGE_RESULT_PATH = OUTPUT_DIR / "QIRA7_BRIDGE_RESULT.json"
ACTION_MANIFEST_AUDIT_PATH = OUTPUT_DIR / "QIRA7_ACTION_MANIFEST_AUDIT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA7_NEXT_STEPS.md"


class QiraCiEvidenceBridgeRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_CiEvidenceBridgeRequest/v0.1", alias="schema")
    packet_path: str = ""
    output_dir: str = str(OUTPUT_DIR)
    source: str = "github_actions"
    workflow_name: str = "QIRA CI Evidence Bridge"
    job_name: str = "qira-ci-evidence"
    check_name: str = "repository CI"
    check_command: str = "python -m pytest"
    check_status: str = "unknown"
    exit_code: int | None = None
    evidence_summary: str = ""
    commit_sha: str = ""
    branch: str = ""
    declared_claims: list[str] = Field(default_factory=lambda: ["Repository-supplied CI evidence for scoped QIRA review only."])


class QiraCiEvidenceBridgeResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_CiEvidenceBridgeResult/v0.1", alias="schema")
    decision: BridgeDecision
    validation_decision: str
    review_decision: str
    release_gate_decision: str | None = None
    packet_path: str
    evidence_path: str
    validation_path: str
    review_path: str
    output_dir: str
    workflow_auto_enabled: bool = False
    active_workflow_created: bool = False
    external_actions_performed: bool = False
    commands_executed_by_qira: bool = False
    github_api_used_by_qira: bool = False
    patch_applied: bool = False
    deploy_performed: bool = False
    token_printed: bool = False
    known_limits: list[str] = Field(default_factory=list)


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


def _resolve_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    if path.is_absolute():
        try:
            return path.relative_to(_repo_root())
        except ValueError as exc:
            raise ValueError("QIRA-7 output directory must be inside the repository.") from exc
    return path


def build_ci_evidence_from_bridge_request(request: QiraCiEvidenceBridgeRequest, packet_id: str | None = None) -> CiEvidencePacket:
    return CiEvidencePacket(
        packet_id=packet_id,
        source="github_actions" if request.source not in {"github_actions", "local_ci", "manual_fixture", "unknown"} else request.source,
        workflow_name=request.workflow_name,
        job_name=request.job_name,
        commit_sha=request.commit_sha,
        branch=request.branch,
        evidence_summary=request.evidence_summary or "Repository-supplied CI status metadata for QIRA review.",
        checks=[
            CiCheckResult(
                name=request.check_name,
                command=request.check_command,
                status=request.check_status if request.check_status in {"pass", "fail", "skipped", "cancelled", "unknown"} else "unknown",
                exit_code=request.exit_code,
                summary=request.evidence_summary,
            )
        ],
        declared_claims=request.declared_claims,
    )


def _bridge_decision(validation_decision: str, review_decision: str) -> BridgeDecision:
    if validation_decision.startswith("BLOCK") or review_decision.startswith("BLOCK"):
        return "BLOCK_QIRA7_CI_EVIDENCE"
    if validation_decision.startswith("HOLD") or review_decision.startswith("HOLD"):
        return "HOLD_QIRA7_CI_EVIDENCE_PARTIAL"
    return "PASS_QIRA7_CI_EVIDENCE_BRIDGE"


def write_next_steps(output_dir: Path = OUTPUT_DIR) -> Path:
    return _write_text(
        output_dir / "QIRA7_NEXT_STEPS.md",
        """# QIRA-7 Next Steps

1. Keep the workflow example in `examples/` until the repository owner opts in.
2. In an enabled repository, run tests with normal CI steps before invoking the bridge.
3. Pass the recorded status and exit code to QIRA-7 as metadata.
4. Publish QIRA artifacts as workflow artifacts only if the repository owner wants them.

QIRA-7 does not run project commands, call GitHub APIs, apply patches, merge, deploy, upload packages, publish registry metadata, or handle tokens.
""",
    )


def run_ci_evidence_bridge(request: QiraCiEvidenceBridgeRequest) -> QiraCiEvidenceBridgeResult:
    output_dir = _resolve_output_dir(request.output_dir)
    if not request.packet_path:
        result = QiraCiEvidenceBridgeResult(
            decision="HOLD_QIRA7_PACKET_REQUIRED",
            validation_decision="not_checked",
            review_decision="not_checked",
            packet_path="",
            evidence_path=str(output_dir / "QIRA7_CI_EVIDENCE.json"),
            validation_path=str(output_dir / "QIRA7_VALIDATION_RESULT.json"),
            review_path=str(output_dir / "QIRA7_REVIEW_RESULT.json"),
            output_dir=str(output_dir),
            known_limits=["A QIRA task packet path is required."],
        )
        _write_json(output_dir / "QIRA7_BRIDGE_RESULT.json", result.model_dump(mode="json", by_alias=True))
        write_next_steps(output_dir)
        return result

    packet_path = Path(request.packet_path)
    if not packet_path.is_absolute():
        packet_path = _repo_root() / packet_path
    packet = load_task_packet(packet_path)
    evidence = build_ci_evidence_from_bridge_request(request, packet.resolved_packet_id())
    review = build_qira6_ci_review(packet, evidence)
    validation = validate_ci_evidence(evidence)
    decision = _bridge_decision(validation.decision, review.decision)

    evidence_path = output_dir / "QIRA7_CI_EVIDENCE.json"
    validation_path = output_dir / "QIRA7_VALIDATION_RESULT.json"
    augmented_path = output_dir / "QIRA7_AUGMENTED_TASK_PACKET.json"
    review_path = output_dir / "QIRA7_REVIEW_RESULT.json"
    bridge_path = output_dir / "QIRA7_BRIDGE_RESULT.json"

    _write_json(evidence_path, evidence.model_dump(mode="json", by_alias=True))
    _write_json(validation_path, validation.model_dump(mode="json", by_alias=True))
    _write_json(augmented_path, review.augmented_packet.model_dump(mode="json", by_alias=True))
    _write_json(review_path, review.model_dump(mode="json", by_alias=True))
    write_next_steps(output_dir)
    result = QiraCiEvidenceBridgeResult(
        decision=decision,
        validation_decision=validation.decision,
        review_decision=review.decision,
        release_gate_decision=review.release_gate_review.get("release_gate_decision"),
        packet_path=str(packet_path).replace("\\", "/"),
        evidence_path=str(evidence_path).replace("\\", "/"),
        validation_path=str(validation_path).replace("\\", "/"),
        review_path=str(review_path).replace("\\", "/"),
        output_dir=str(output_dir).replace("\\", "/"),
        known_limits=[
            "QIRA-7 converts opt-in workflow metadata into QIRA CI evidence JSON.",
            "QIRA-7 does not execute project commands; tests must run in normal repository CI steps.",
            "QIRA-7 does not call GitHub APIs, apply patches, merge, deploy, upload, publish, or handle tokens.",
            "A bridge pass is not security certification, quality guarantee, production readiness, or action authorization.",
        ],
    )
    _write_json(bridge_path, result.model_dump(mode="json", by_alias=True))
    return result


def run_sample() -> QiraCiEvidenceBridgeResult:
    generated = generate_packet_from_request(sample_generation_request())
    _write_json(SAMPLE_PACKET_PATH, generated.packet.model_dump(mode="json", by_alias=True))
    request = QiraCiEvidenceBridgeRequest(
        packet_path=str(SAMPLE_PACKET_PATH),
        output_dir=str(OUTPUT_DIR),
        check_name="qira7 targeted pytest",
        check_command="python -m pytest tests/test_qira_ci_evidence.py tests/test_qira_ci_evidence_cli.py",
        check_status="pass",
        exit_code=0,
        evidence_summary="Repository-owned CI metadata reports QIRA evidence intake tests passed.",
        commit_sha="local-fixture",
        branch="sample",
    )
    return run_ci_evidence_bridge(request)


def audit_qira7_action_manifest() -> dict[str, Any]:
    paths = [
        _repo_root() / ".github" / "actions" / "qira-ci-evidence-bridge" / "action.yml",
        _repo_root() / "examples" / "qira_ci_evidence_bridge_workflow.yml",
    ]
    forbidden = ["twine upload", "mcp-publisher publish", "git push", "gh release", "curl ", "wget "]
    findings: list[str] = []
    for path in paths:
        if not path.exists():
            findings.append(f"missing:{path.relative_to(_repo_root())}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        findings.extend(f"{path.relative_to(_repo_root())}:{item}" for item in forbidden if item in text)
    active_workflow = (_repo_root() / ".github" / "workflows" / "qira-ci-evidence-bridge.yml").exists()
    result = {
        "decision": "PASS_QIRA7_ACTION_MANIFEST_SAFE" if not findings and not active_workflow else "BLOCK_QIRA7_ACTION_MANIFEST_UNSAFE",
        "manifest_exists": paths[0].exists(),
        "example_workflow_exists": paths[1].exists(),
        "active_workflow_created": active_workflow,
        "workflow_auto_enabled": False,
        "forbidden_command_findings": findings,
        "external_actions_performed": False,
        "token_printed": False,
    }
    _write_json(ACTION_MANIFEST_AUDIT_PATH, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bridge opt-in GitHub Action metadata to QIRA CI evidence.")
    parser.add_argument("--run-sample", action="store_true", help="Write and review a safe QIRA-7 sample.")
    parser.add_argument("--audit-manifest", action="store_true", help="Audit QIRA-7 action and example workflow manifests.")
    parser.add_argument("--packet", default="", help="Path to a QIRA task packet JSON file.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Output directory for QIRA-7 artifacts.")
    parser.add_argument("--check-name", default="repository CI")
    parser.add_argument("--check-command", default="python -m pytest")
    parser.add_argument("--check-status", default="unknown", choices=["pass", "fail", "skipped", "cancelled", "unknown"])
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--evidence-summary", default="")
    parser.add_argument("--workflow-name", default="QIRA CI Evidence Bridge")
    parser.add_argument("--job-name", default="qira-ci-evidence")
    parser.add_argument("--commit-sha", default="")
    parser.add_argument("--branch", default="")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_manifest:
        result = audit_qira7_action_manifest()
        print(f"qira7_action_manifest_audit: {result['decision']}")
        return
    if args.run_sample:
        result = run_sample()
    else:
        result = run_ci_evidence_bridge(
            QiraCiEvidenceBridgeRequest(
                packet_path=args.packet,
                output_dir=args.output_dir,
                workflow_name=args.workflow_name,
                job_name=args.job_name,
                check_name=args.check_name,
                check_command=args.check_command,
                check_status=args.check_status,
                exit_code=args.exit_code,
                evidence_summary=args.evidence_summary,
                commit_sha=args.commit_sha,
                branch=args.branch,
            )
        )
    print(f"qira_ci_evidence_bridge: {result.decision} validation={result.validation_decision}")


if __name__ == "__main__":
    main()
