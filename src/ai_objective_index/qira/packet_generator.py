from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .diff_classifier import PatchDiffClassificationReport, classify_patch_paths
from .input_packet import QiraTaskPacket, extract_changed_files_from_diff
from .models import EvidenceOrigin, PatchAction


PacketGenerationDecision = Literal[
    "PASS_QIRA_PACKET_GENERATED",
    "HOLD_NO_CHANGED_FILES",
    "HOLD_PATH_REVIEW",
    "BLOCK_FORBIDDEN_PATH",
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _stable_id(prefix: str, *parts: object) -> str:
    text = "::".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


class QiraPacketGenerationRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_PacketGenerationRequest/v0.1", alias="schema")
    task: str
    patch_summary: str = ""
    repo_scope: str = "github_pr_or_local_diff"
    changed_files: list[str] = Field(default_factory=list)
    patch_diff: str = ""
    test_commands: list[str] = Field(default_factory=list)
    tests_passed: bool = False
    test_summary: str = ""
    evidence_origin: EvidenceOrigin = "unknown"
    declared_claims: list[str] = Field(default_factory=list)
    requested_action: PatchAction = "pr_open"
    forbidden_changes: list[str] = Field(default_factory=lambda: [".env", ".pypirc", "credentials", "secrets"])


class QiraPacketGenerationResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_PacketGenerationResult/v0.1", alias="schema")
    decision: PacketGenerationDecision
    packet: QiraTaskPacket
    changed_files: list[str] = Field(default_factory=list)
    inferred_expected_behavior: list[str] = Field(default_factory=list)
    path_classification_decision: str
    path_classification: PatchDiffClassificationReport
    known_limits: list[str] = Field(default_factory=list)
    external_actions_performed: bool = False
    git_command_executed: bool = False
    github_api_used: bool = False
    tests_executed: bool = False
    patch_applied: bool = False
    token_printed: bool = False
    generated_at: str = Field(default_factory=_timestamp)


def _normalize_changed_files(request: QiraPacketGenerationRequest) -> list[str]:
    paths = list(request.changed_files)
    if not paths and request.patch_diff:
        paths = extract_changed_files_from_diff(request.patch_diff)
    return sorted({path.replace("\\", "/").strip() for path in paths if path.strip()})


def infer_expected_behavior(task: str, changed_files: list[str], category_counts: dict[str, int]) -> list[str]:
    clauses = [
        f"Implement the requested task without expanding scope: {task}",
        "Preserve existing public claim boundaries and do not add verification, security-certification, quality-guarantee, production-readiness, deployment-approval, or action-authorization claims.",
    ]
    if category_counts.get("source"):
        clauses.append("Source changes should preserve documented behavior unless the task explicitly states a behavior change.")
    if category_counts.get("test"):
        clauses.append("Test changes should cover the intended behavior and avoid replacing evidence with unsupported claims.")
    if category_counts.get("docs"):
        clauses.append("Documentation changes should match implementation boundaries and limitations.")
    if category_counts.get("config") or category_counts.get("dependency") or category_counts.get("ci"):
        clauses.append("Configuration, dependency, or CI changes require reviewer attention before merge.")
    if category_counts.get("data_or_generated"):
        clauses.append("Generated or data artifact changes should remain reproducible and free of secrets.")
    if category_counts.get("unknown"):
        clauses.append("Unclassified changed paths require manual review before merge.")
    if not changed_files:
        clauses.append("Changed files are missing, so the packet can only be used as a draft intake record.")
    clauses.append("Do not deploy, publish, upload packages, submit registry metadata, or run external actions from this packet.")
    return clauses


def _decision_from_path_report(path_report: PatchDiffClassificationReport) -> PacketGenerationDecision:
    if path_report.decision.startswith("BLOCK"):
        return "BLOCK_FORBIDDEN_PATH"
    if path_report.decision == "HOLD_NO_CHANGED_FILES":
        return "HOLD_NO_CHANGED_FILES"
    if path_report.decision.startswith("HOLD"):
        return "HOLD_PATH_REVIEW"
    return "PASS_QIRA_PACKET_GENERATED"


def generate_packet_from_request(request: QiraPacketGenerationRequest) -> QiraPacketGenerationResult:
    changed_files = _normalize_changed_files(request)
    path_report = classify_patch_paths(
        changed_files=changed_files,
        patch_diff=request.patch_diff,
        forbidden_changes=request.forbidden_changes,
    )
    expected_behavior = infer_expected_behavior(request.task, changed_files, path_report.category_counts)
    packet = QiraTaskPacket(
        packet_id=_stable_id("qira-generated-packet", request.task, request.patch_summary, changed_files, request.patch_diff),
        task=request.task,
        repo_scope=request.repo_scope,
        expected_behavior=expected_behavior,
        changed_files=changed_files,
        patch_summary=request.patch_summary or "Generated from local PR diff or changed-file metadata.",
        patch_diff=request.patch_diff,
        tests_passed=request.tests_passed,
        test_commands=request.test_commands,
        test_summary=request.test_summary,
        evidence_origin=request.evidence_origin,
        requested_action=request.requested_action,
        declared_claims=request.declared_claims,
        forbidden_changes=request.forbidden_changes,
        packet_generation_source="local_diff_or_changed_files",
        generated_by="qira5_packet_generator",
    )
    decision = _decision_from_path_report(path_report)
    return QiraPacketGenerationResult(
        decision=decision,
        packet=packet,
        changed_files=changed_files,
        inferred_expected_behavior=expected_behavior,
        path_classification_decision=path_report.decision,
        path_classification=path_report,
        known_limits=[
            "QIRA-5 reads local diff text or changed-file metadata only.",
            "QIRA-5 does not call GitHub APIs, run git commands, apply patches, execute tests, deploy, upload, or publish.",
            "Generated packets can support review intake, but they do not verify code, certify security, guarantee quality, or authorize release actions.",
        ],
    )


def sample_pr_diff() -> str:
    return """diff --git a/src/ai_objective_index/qira/packet_generator.py b/src/ai_objective_index/qira/packet_generator.py
--- a/src/ai_objective_index/qira/packet_generator.py
+++ b/src/ai_objective_index/qira/packet_generator.py
@@ -0,0 +1,5 @@
+# local packet generator fixture
diff --git a/tests/test_qira_packet_generator.py b/tests/test_qira_packet_generator.py
--- a/tests/test_qira_packet_generator.py
+++ b/tests/test_qira_packet_generator.py
@@ -0,0 +1,5 @@
+# local packet generator tests fixture
diff --git a/docs/qira5_pr_packet_generator.md b/docs/qira5_pr_packet_generator.md
--- a/docs/qira5_pr_packet_generator.md
+++ b/docs/qira5_pr_packet_generator.md
@@ -0,0 +1,5 @@
+# local packet generator docs fixture
"""


def sample_generation_request() -> QiraPacketGenerationRequest:
    return QiraPacketGenerationRequest(
        task="Generate a conservative QIRA task packet from local PR diff metadata.",
        patch_summary="Adds a local packet generator and CLI demo for PR-style diffs.",
        patch_diff=sample_pr_diff(),
        test_commands=["python -m pytest tests/test_qira_packet_generator.py tests/test_qira_pr_packet_cli.py"],
        tests_passed=False,
        test_summary="Tests are listed for reviewer/CI use, but QIRA-5 did not execute them.",
        evidence_origin="unknown",
        requested_action="pr_open",
        declared_claims=["Local packet generation only; no tests executed by QIRA-5."],
    )
