from __future__ import annotations

import hashlib
import re
from pathlib import Path

from ai_objective_index.qira.input_packet import extract_changed_files_from_diff

from .qira_pilot_receipt import QIRAPatchClassification


SAMPLE_PATCH_DIFF = """diff --git a/docs/qira_local_review.md b/docs/qira_local_review.md
index 0000000..1111111 100644
--- a/docs/qira_local_review.md
+++ b/docs/qira_local_review.md
@@ -0,0 +1,3 @@
+# QIRA local review
+This sample records a local review artifact only.
diff --git a/tests/test_qira_local_review.py b/tests/test_qira_local_review.py
index 0000000..2222222 100644
--- a/tests/test_qira_local_review.py
+++ b/tests/test_qira_local_review.py
@@ -0,0 +1,3 @@
+def test_sample_review():
+    assert True
diff --git a/scripts/deploy_release.ps1 b/scripts/deploy_release.ps1
index 0000000..3333333 100644
--- a/scripts/deploy_release.ps1
+++ b/scripts/deploy_release.ps1
@@ -0,0 +1,2 @@
+# Negative-control fixture: deploy step must not be authorized by QIRA.
+Write-Output "deploy blocked by local pilot review"
"""


def stable_id(prefix: str, *parts: object) -> str:
    text = "::".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _category_for_path(path: str) -> str:
    lowered = path.replace("\\", "/").lower()
    name = Path(lowered).name
    if lowered.startswith("tests/") or name.startswith("test_"):
        return "tests"
    if lowered.startswith("docs/") or lowered.endswith((".md", ".rst", ".txt")):
        return "docs"
    if lowered.startswith(".github/workflows/"):
        return "ci"
    if name in {"pyproject.toml", "requirements.txt", "setup.cfg"}:
        return "packaging"
    if "deploy" in lowered or "release" in lowered:
        return "security_sensitive"
    if lowered.endswith((".py", ".ts", ".js", ".tsx", ".jsx")):
        return "source"
    if lowered.endswith((".yml", ".yaml", ".toml", ".ini", ".cfg")):
        return "config"
    return "unknown"


def _risk_flags(paths: list[str], patch_text: str) -> list[str]:
    flags: set[str] = set()
    lowered_patch = patch_text.lower()
    for path in paths:
        lowered = path.replace("\\", "/").lower()
        if any(marker in lowered for marker in [".env", ".pypirc", "secret", "token", "credential"]):
            flags.add("auth_or_token_handling")
        if lowered.endswith(("requirements.txt", "pyproject.toml", "package.json", "uv.lock")):
            flags.add("dependency_change")
        if lowered.startswith(".github/workflows/") or "deploy" in lowered or "release" in lowered:
            flags.add("release_config_change")
        if lowered.endswith((".ps1", ".sh", ".bat", ".cmd")):
            flags.add("subprocess_or_shell")
        if lowered.startswith("src/"):
            flags.add("generated_code")
    if any(term in lowered_patch for term in ["requests.", "http://", "https://"]):
        flags.add("network_behavior")
    if any(term in lowered_patch for term in ["open(", "write_text", "remove-item", "rm -"]):
        flags.add("filesystem_write")
    if len(paths) > 10:
        flags.add("large_diff")
    return sorted(flags) or ["unknown"]


def classify_qira_patch(task_id: str, patch_text: str = "", changed_files: list[str] | None = None) -> QIRAPatchClassification:
    paths = list(changed_files or [])
    if not paths and patch_text:
        paths = extract_changed_files_from_diff(patch_text)
    categories = sorted({_category_for_path(path) for path in paths})
    flags = _risk_flags(paths, patch_text)
    if any(flag in flags for flag in ["auth_or_token_handling"]):
        decision = "BLOCK_SECRET_RISK"
        explanation = "Patch touches token/secret-like paths or content."
    elif "release_config_change" in flags:
        decision = "BLOCK_FORBIDDEN_ACTION"
        explanation = "Patch includes release/deploy negative-control surface that cannot be authorized by a local QIRA pilot."
    elif "dependency_change" in flags:
        decision = "HOLD_SECURITY_REVIEW"
        explanation = "Dependency or packaging surface needs reviewer attention."
    elif "unknown" in categories:
        decision = "HOLD_NEEDS_OWNER_REVIEW"
        explanation = "Unknown file category needs owner review."
    else:
        decision = "ALLOW_REVIEW"
        explanation = "Patch scope is limited to local docs/tests review surfaces."
    return QIRAPatchClassification(
        patch_id=stable_id("qira-patch", task_id, paths, flags),
        task_id=task_id,
        files_changed_count=len(paths),
        file_categories=categories,
        risk_flags=flags,
        classification_decision=decision,  # type: ignore[arg-type]
        evidence_refs=[f"local_patch#{index}" for index, _path in enumerate(paths, start=1)],
        explanation=explanation,
        next_actions=[
            "review HOLD/BLOCK findings before merge or deploy decisions",
            "request independent CI evidence for any real owner-consented pilot",
        ],
    )


def sample_patch_classification(task_id: str) -> QIRAPatchClassification:
    return classify_qira_patch(task_id=task_id, patch_text=SAMPLE_PATCH_DIFF)
