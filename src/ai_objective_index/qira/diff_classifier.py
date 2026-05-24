from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .input_packet import extract_changed_files_from_diff


PathCategory = Literal[
    "source",
    "test",
    "docs",
    "config",
    "ci",
    "dependency",
    "data_or_generated",
    "private_or_secret",
    "path_escape",
    "unknown",
]
PathRisk = Literal["LOW", "MEDIUM", "HIGH", "BLOCK"]


PATH_ESCAPE_PATTERNS = [
    re.compile(r"(^|[\\/])\.\.([\\/]|$)"),
    re.compile(r"^[A-Za-z]:[\\/]"),
    re.compile(r"^/"),
]
SECRET_MARKERS = [".env", ".pypirc", "credential", "secret", "token", "private_key"]
DEPENDENCY_FILES = {
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "poetry.lock",
    "uv.lock",
    "pnpm-lock.yaml",
}
CONFIG_FILES = {
    "setup.cfg",
    "tox.ini",
    "mypy.ini",
    "ruff.toml",
    ".pre-commit-config.yaml",
}


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


class ChangedFileClassification(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_ChangedFileClassification/v0.1", alias="schema")
    path: str
    category: PathCategory
    risk: PathRisk
    reasons: list[str] = Field(default_factory=list)


class PatchDiffClassificationReport(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_PatchDiffClassificationReport/v0.1", alias="schema")
    decision: str
    changed_file_count: int
    classifications: list[ChangedFileClassification]
    category_counts: dict[str, int] = Field(default_factory=dict)
    risk_counts: dict[str, int] = Field(default_factory=dict)
    block_reasons: list[str] = Field(default_factory=list)
    hold_reasons: list[str] = Field(default_factory=list)
    external_actions_performed: bool = False
    patch_applied: bool = False
    tests_executed: bool = False
    token_printed: bool = False
    generated_at: str = Field(default_factory=_timestamp)


def _is_path_escape(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(pattern.search(normalized) for pattern in PATH_ESCAPE_PATTERNS)


def classify_changed_file(path: str, forbidden_changes: list[str] | None = None) -> ChangedFileClassification:
    normalized = path.replace("\\", "/").strip()
    lowered = normalized.lower()
    name = Path(normalized).name.lower()
    forbidden = [item.lower() for item in (forbidden_changes or [])]
    reasons: list[str] = []

    if _is_path_escape(normalized):
        return ChangedFileClassification(path=path, category="path_escape", risk="BLOCK", reasons=["path escapes repository-relative scope"])
    if any(marker in lowered for marker in SECRET_MARKERS) or any(marker and marker in lowered for marker in forbidden):
        return ChangedFileClassification(path=path, category="private_or_secret", risk="BLOCK", reasons=["path matches private/credential/secret marker"])

    if lowered.startswith(".github/workflows/"):
        return ChangedFileClassification(path=path, category="ci", risk="MEDIUM", reasons=["CI workflow change needs review"])
    if name in DEPENDENCY_FILES:
        return ChangedFileClassification(path=path, category="dependency", risk="MEDIUM", reasons=["dependency or packaging surface changed"])
    if name in CONFIG_FILES or lowered.endswith((".yaml", ".yml", ".toml", ".ini", ".cfg")):
        return ChangedFileClassification(path=path, category="config", risk="MEDIUM", reasons=["configuration surface changed"])
    if lowered.startswith(("data/", "public_launch/", "release/", "dist/")):
        return ChangedFileClassification(path=path, category="data_or_generated", risk="MEDIUM", reasons=["data/generated/release artifact changed"])
    if lowered.startswith(("tests/", "test/")) or name.startswith("test_") or lowered.endswith(("_test.py", ".test.ts", ".spec.ts")):
        return ChangedFileClassification(path=path, category="test", risk="LOW", reasons=["test surface changed"])
    if lowered.startswith(("docs/", "README".lower())) or lowered.endswith((".md", ".rst", ".txt")):
        return ChangedFileClassification(path=path, category="docs", risk="LOW", reasons=["documentation surface changed"])
    if lowered.startswith(("src/", "app/", "lib/")) or lowered.endswith((".py", ".ts", ".js", ".tsx", ".jsx")):
        return ChangedFileClassification(path=path, category="source", risk="LOW", reasons=["source surface changed"])
    return ChangedFileClassification(path=path, category="unknown", risk="MEDIUM", reasons=["unclassified path needs review"])


def classify_patch_paths(
    changed_files: list[str] | None = None,
    patch_diff: str = "",
    forbidden_changes: list[str] | None = None,
) -> PatchDiffClassificationReport:
    paths = list(changed_files or [])
    if not paths and patch_diff:
        paths = extract_changed_files_from_diff(patch_diff)
    classifications = [classify_changed_file(path, forbidden_changes=forbidden_changes) for path in paths]
    category_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    block_reasons: list[str] = []
    hold_reasons: list[str] = []
    for item in classifications:
        category_counts[item.category] = category_counts.get(item.category, 0) + 1
        risk_counts[item.risk] = risk_counts.get(item.risk, 0) + 1
        if item.risk == "BLOCK":
            block_reasons.extend(f"{item.path}: {reason}" for reason in item.reasons)
        elif item.risk in {"HIGH", "MEDIUM"}:
            hold_reasons.extend(f"{item.path}: {reason}" for reason in item.reasons)
    if block_reasons:
        decision = "BLOCK_PATH_CLASSIFICATION"
    elif not classifications:
        decision = "HOLD_NO_CHANGED_FILES"
        hold_reasons.append("No changed files or diff paths were provided.")
    elif hold_reasons:
        decision = "HOLD_PATH_REVIEW"
    else:
        decision = "PASS_PATH_CLASSIFICATION"
    return PatchDiffClassificationReport(
        decision=decision,
        changed_file_count=len(classifications),
        classifications=classifications,
        category_counts=category_counts,
        risk_counts=risk_counts,
        block_reasons=block_reasons,
        hold_reasons=hold_reasons,
    )
