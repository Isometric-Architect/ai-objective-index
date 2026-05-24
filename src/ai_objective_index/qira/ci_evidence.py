from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .input_packet import QiraTaskPacket
from .releasegate import detect_unsupported_claims
from .test_command_contract import build_test_command_contract


CiCheckStatus = Literal["pass", "fail", "skipped", "cancelled", "unknown"]
CiEvidenceSource = Literal["github_actions", "local_ci", "manual_fixture", "unknown"]
CiEvidenceDecision = Literal[
    "PASS_CI_EVIDENCE_ACCEPTED",
    "HOLD_CI_EVIDENCE_MISSING",
    "HOLD_CI_EVIDENCE_PARTIAL",
    "BLOCK_CI_EVIDENCE_FAILED",
    "BLOCK_CI_COMMAND_UNSAFE",
    "BLOCK_UNSUPPORTED_CLAIM",
    "BLOCK_SECRET_IN_EVIDENCE",
]


TOKEN_PATTERNS = [
    re.compile(r"\bpypi-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9._-]{12,}"),
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _stable_id(prefix: str, *parts: object) -> str:
    text = "::".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _contains_token_like(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        return any(_contains_token_like(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_token_like(item) for item in value.values())
    text = str(value)
    return any(pattern.search(text) for pattern in TOKEN_PATTERNS)


class CiCheckResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_CiCheckResult/v0.1", alias="schema")
    name: str
    command: str
    status: CiCheckStatus = "unknown"
    exit_code: int | None = None
    summary: str = ""
    duration_seconds: float | None = None
    artifact_refs: list[str] = Field(default_factory=list)
    log_excerpt: str = ""


class CiEvidencePacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_CiEvidencePacket/v0.1", alias="schema")
    evidence_id: str | None = None
    packet_id: str | None = None
    source: CiEvidenceSource = "unknown"
    workflow_name: str = ""
    job_name: str = ""
    commit_sha: str = ""
    branch: str = ""
    checks: list[CiCheckResult] = Field(default_factory=list)
    declared_claims: list[str] = Field(default_factory=list)
    evidence_summary: str = ""
    submitted_at: str = Field(default_factory=_timestamp)
    external_actions_performed_by_qira: bool = False
    commands_executed_by_qira: bool = False
    github_api_used_by_qira: bool = False
    token_printed: bool = False

    def resolved_evidence_id(self) -> str:
        return self.evidence_id or _stable_id("qira-ci-evidence", self.packet_id, self.source, self.workflow_name, self.job_name, self.checks)


class CiEvidenceValidationResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_CiEvidenceValidationResult/v0.1", alias="schema")
    evidence_id: str
    decision: CiEvidenceDecision
    tests_passed: bool = False
    accepted_command_count: int = 0
    failed_check_names: list[str] = Field(default_factory=list)
    hold_check_names: list[str] = Field(default_factory=list)
    block_reasons: list[str] = Field(default_factory=list)
    hold_reasons: list[str] = Field(default_factory=list)
    command_contract_decision: str
    can_support_patch_draft: bool = False
    can_support_pr_open: bool = False
    can_authorize_merge: bool = False
    can_authorize_deploy: bool = False
    can_certify_security: bool = False
    can_guarantee_quality: bool = False
    known_limits: list[str] = Field(default_factory=list)
    external_actions_performed_by_qira: bool = False
    commands_executed_by_qira: bool = False
    github_api_used_by_qira: bool = False
    token_printed: bool = False
    generated_at: str = Field(default_factory=_timestamp)


class Qira6CiEvidenceReviewResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_CiEvidenceReviewResult/v0.1", alias="schema")
    decision: str
    validation: CiEvidenceValidationResult
    release_gate_review: dict
    augmented_packet: QiraTaskPacket
    external_actions_performed: bool = False
    commands_executed_by_qira: bool = False
    github_api_used_by_qira: bool = False
    patch_applied: bool = False
    deploy_performed: bool = False
    token_printed: bool = False
    generated_at: str = Field(default_factory=_timestamp)


def validate_ci_evidence(evidence: CiEvidencePacket) -> CiEvidenceValidationResult:
    evidence_id = evidence.resolved_evidence_id()
    commands = [check.command for check in evidence.checks if check.command.strip()]
    command_contract = build_test_command_contract(commands)
    block_reasons: list[str] = []
    hold_reasons: list[str] = []
    failed: list[str] = []
    held: list[str] = []

    if _contains_token_like(evidence.model_dump(mode="json", by_alias=True)):
        block_reasons.append("Evidence contains token-like or secret-like text.")
        decision: CiEvidenceDecision = "BLOCK_SECRET_IN_EVIDENCE"
    elif detect_unsupported_claims(evidence.declared_claims):
        block_reasons.append("Evidence declares unsupported verification, safety, security, quality, readiness, or authorization claims.")
        decision = "BLOCK_UNSUPPORTED_CLAIM"
    elif command_contract.decision.startswith("BLOCK"):
        block_reasons.extend(command_contract.block_reasons)
        decision = "BLOCK_CI_COMMAND_UNSAFE"
    elif not evidence.checks:
        hold_reasons.append("No CI checks were supplied.")
        decision = "HOLD_CI_EVIDENCE_MISSING"
    else:
        for check in evidence.checks:
            if check.status in {"fail", "cancelled"} or (check.exit_code is not None and check.exit_code != 0):
                failed.append(check.name)
            elif check.status in {"skipped", "unknown"}:
                held.append(check.name)
        if failed:
            block_reasons.extend(f"{name}: check did not pass" for name in failed)
            decision = "BLOCK_CI_EVIDENCE_FAILED"
        elif held or command_contract.decision.startswith("HOLD"):
            hold_reasons.extend(command_contract.hold_reasons)
            if held:
                hold_reasons.extend(f"{name}: check status is skipped or unknown" for name in held)
            decision = "HOLD_CI_EVIDENCE_PARTIAL"
        else:
            decision = "PASS_CI_EVIDENCE_ACCEPTED"

    tests_passed = decision == "PASS_CI_EVIDENCE_ACCEPTED"
    return CiEvidenceValidationResult(
        evidence_id=evidence_id,
        decision=decision,
        tests_passed=tests_passed,
        accepted_command_count=len(commands) if tests_passed else 0,
        failed_check_names=failed,
        hold_check_names=held,
        block_reasons=block_reasons,
        hold_reasons=hold_reasons,
        command_contract_decision=command_contract.decision,
        can_support_patch_draft=decision in {"PASS_CI_EVIDENCE_ACCEPTED", "HOLD_CI_EVIDENCE_PARTIAL"},
        can_support_pr_open=tests_passed,
        known_limits=[
            "CI evidence is externally supplied metadata; QIRA does not execute commands or inspect live CI systems.",
            "A CI pass can close a local test-evidence gap for scoped review, but it does not authorize merge, deploy, package upload, registry submission, or public readiness claims.",
            "CI evidence is not security certification, quality guarantee, legal compliance, or production readiness.",
        ],
    )


def apply_ci_evidence_to_packet(packet: QiraTaskPacket, evidence: CiEvidencePacket, validation: CiEvidenceValidationResult) -> QiraTaskPacket:
    if validation.decision != "PASS_CI_EVIDENCE_ACCEPTED":
        return packet.model_copy(deep=True)
    commands = [check.command for check in evidence.checks if check.command.strip()]
    names = ", ".join(check.name for check in evidence.checks) or "CI checks"
    summaries = [check.summary for check in evidence.checks if check.summary.strip()]
    summary = evidence.evidence_summary or f"CI evidence accepted for: {names}."
    if summaries:
        summary = f"{summary} " + " ".join(summaries)
    return packet.model_copy(
        deep=True,
        update={
            "tests_passed": True,
            "test_commands": sorted(set(list(packet.test_commands) + commands)),
            "test_summary": summary,
            "evidence_origin": "ci_fixture",
            "ci_evidence_id": validation.evidence_id,
            "ci_evidence_source": evidence.source,
        },
    )


def build_qira6_ci_review(packet: QiraTaskPacket, evidence: CiEvidencePacket) -> Qira6CiEvidenceReviewResult:
    from .review_cli import build_qira3_review

    validation = validate_ci_evidence(evidence)
    augmented = apply_ci_evidence_to_packet(packet, evidence, validation)
    review = build_qira3_review(augmented)
    review.pop("_release_report", None)
    review.pop("_path_report", None)
    review.pop("_command_contract", None)
    if validation.decision.startswith("BLOCK"):
        decision = "BLOCK_QIRA6_CI_EVIDENCE"
    elif validation.decision.startswith("HOLD"):
        decision = "HOLD_QIRA6_CI_EVIDENCE"
    else:
        decision = review["decision"].replace("QIRA3", "QIRA6")
    return Qira6CiEvidenceReviewResult(
        decision=decision,
        validation=validation,
        release_gate_review=review,
        augmented_packet=augmented,
    )


def sample_ci_evidence_packet(packet_id: str | None = None) -> CiEvidencePacket:
    return CiEvidencePacket(
        evidence_id="qira-ci-evidence-sample-pass",
        packet_id=packet_id,
        source="github_actions",
        workflow_name="QIRA local release gate",
        job_name="qira-dry-run",
        commit_sha="local-fixture",
        branch="sample",
        evidence_summary="Repository-owned CI fixture reports local QIRA-5 packet generator tests passed.",
        checks=[
            CiCheckResult(
                name="qira5 targeted pytest",
                command="python -m pytest tests/test_qira_packet_generator.py tests/test_qira_pr_packet_cli.py",
                status="pass",
                exit_code=0,
                summary="Targeted QIRA-5 tests passed in CI fixture metadata.",
            )
        ],
        declared_claims=["Scoped CI evidence accepted for local QIRA review only."],
    )
