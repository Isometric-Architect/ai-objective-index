from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import EvidenceOrigin, PatchAction


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _stable_id(prefix: str, *parts: object) -> str:
    text = "::".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


class QiraTaskPacket(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_TaskPacket/v0.1", alias="schema")
    packet_id: str | None = None
    task: str
    repo_scope: str = "local_or_fixture_repo"
    expected_behavior: list[str] = Field(default_factory=list)
    changed_files: list[str] = Field(default_factory=list)
    patch_summary: str = ""
    patch_diff: str = ""
    tests_passed: bool = False
    test_summary: str = ""
    evidence_origin: EvidenceOrigin = "unknown"
    requested_action: PatchAction = "patch_draft"
    declared_claims: list[str] = Field(default_factory=list)
    forbidden_changes: list[str] = Field(default_factory=lambda: [".env", ".pypirc", "credentials", "secrets"])
    created_at: str = Field(default_factory=_timestamp)

    def resolved_packet_id(self) -> str:
        return self.packet_id or _stable_id("qira-task", self.task, self.patch_summary, self.changed_files, self.patch_diff)


DIFF_FILE_PATTERNS = [
    re.compile(r"^\+\+\+\s+b/(.+)$"),
    re.compile(r"^---\s+a/(.+)$"),
    re.compile(r"^diff\s+--git\s+a/(.+?)\s+b/(.+)$"),
]


def extract_changed_files_from_diff(diff_text: str) -> list[str]:
    files: list[str] = []
    for line in diff_text.splitlines():
        stripped = line.strip()
        for pattern in DIFF_FILE_PATTERNS:
            match = pattern.match(stripped)
            if not match:
                continue
            groups = [item for item in match.groups() if item and item != "/dev/null"]
            files.extend(groups)
    return sorted(set(files))


def packet_to_contract_and_patch(packet: QiraTaskPacket) -> tuple[dict[str, Any], dict[str, Any]]:
    from .releasegate import _stable_id as releasegate_stable_id

    packet_id = packet.resolved_packet_id()
    changed_files = list(packet.changed_files)
    if not changed_files and packet.patch_diff:
        changed_files = extract_changed_files_from_diff(packet.patch_diff)
    contract_payload = {
        "contract_id": releasegate_stable_id("qira-contract", packet_id, packet.task, packet.expected_behavior),
        "task": packet.task,
        "repo_scope": packet.repo_scope,
        "expected_behavior": packet.expected_behavior,
        "forbidden_changes": packet.forbidden_changes,
    }
    patch_payload = {
        "patch_id": releasegate_stable_id("qira-patch", packet_id, packet.patch_summary, changed_files),
        "contract_id": contract_payload["contract_id"],
        "summary": packet.patch_summary or "User-supplied local task packet",
        "changed_files": changed_files,
        "tests_passed": packet.tests_passed,
        "test_summary": packet.test_summary,
        "evidence_origin": packet.evidence_origin,
        "requested_action": packet.requested_action,
        "declared_claims": packet.declared_claims,
    }
    return contract_payload, patch_payload


def sample_task_packet() -> QiraTaskPacket:
    return QiraTaskPacket(
        packet_id="qira-task-sample-local-cli",
        task="Add a local-only QIRA task packet CLI without external execution.",
        expected_behavior=[
            "CLI reads a user-supplied JSON task packet.",
            "CLI derives changed files from packet metadata or patch diff.",
            "CLI writes a local release-gate report.",
            "CLI does not execute tests, deploy, or contact external services.",
        ],
        patch_summary="Adds packet intake helpers and local report writing.",
        patch_diff="""diff --git a/src/ai_objective_index/qira/task_cli.py b/src/ai_objective_index/qira/task_cli.py
--- a/src/ai_objective_index/qira/task_cli.py
+++ b/src/ai_objective_index/qira/task_cli.py
@@ -0,0 +1,5 @@
+# local fixture patch
diff --git a/tests/test_qira_task_cli.py b/tests/test_qira_task_cli.py
--- a/tests/test_qira_task_cli.py
+++ b/tests/test_qira_task_cli.py
@@ -0,0 +1,5 @@
+# local fixture test
""",
        tests_passed=True,
        test_summary="QIRA packet fixture tests passed locally.",
        evidence_origin="local_fixture",
        requested_action="pr_open",
        declared_claims=["Scoped local packet intake passed."],
    )
