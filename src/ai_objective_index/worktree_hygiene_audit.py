from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .public_ops_baseline import OUTPUT_DIR


JSON_OUTPUT_PATH = OUTPUT_DIR / "WORKTREE_HYGIENE_AUDIT_v0_1.json"
MD_OUTPUT_PATH = OUTPUT_DIR / "WORKTREE_CLASSIFICATION.md"
SIZE_REVIEW_BYTES = 5 * 1024 * 1024

SECRETISH_PATTERN = re.compile(
    r"(?:^|[/\\])(?:\.env(?:\..*)?|credentials?(?:\..*)?|secrets?(?:\..*)?|token(?:\..*)?|password(?:\..*)?|private_key(?:\..*)?)$",
    re.IGNORECASE,
)

PACKAGE_8M_FILES = {
    ".gitignore",
    "README.md",
    "CHANGELOG.md",
    "docs/community_launch.md",
    "docs/github_issue_loop_operations.md",
    "docs/issue_feedback_after_public.md",
    "docs/launch_notes.md",
    "docs/manual_publish_checklist.md",
    "docs/package_8m_public_ops_baseline.md",
    "docs/post_public_observation.md",
    "docs/public_beta_release_plan.md",
    "docs/public_metrics_baseline.md",
    "docs/worktree_hygiene_policy.md",
    "src/ai_objective_index/public_ops_baseline.py",
    "src/ai_objective_index/worktree_hygiene_audit.py",
    "src/ai_objective_index/github_issue_labels.py",
    "src/ai_objective_index/observation_log.py",
    "src/ai_objective_index/release_next_decision_gate.py",
    "tests/test_public_ops_baseline.py",
    "tests/test_worktree_hygiene_audit.py",
    "tests/test_github_issue_labels.py",
    "tests/test_observation_log.py",
    "tests/test_release_next_decision_gate.py",
    "tests/test_public_ops_assets.py",
    "data/generated/no_secrets_audit_result_v0_2.json",
    "data/generated/launch_claim_guard_result_v0_2.json",
    "public_launch/POST_PUBLIC_STABILIZATION_RESULT.json",
    "public_launch/PUBLIC_ISSUE_LOOP_RESULT.json",
    "public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _run(command: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}


def _git(args: list[str], runner: Callable[[list[str], int], dict[str, Any]] = _run) -> dict[str, Any]:
    return runner(["git", "-c", f"safe.directory={_repo_root().as_posix()}", *args], 60)


def parse_status_paths(status_text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw in status_text.splitlines():
        if not raw.strip():
            continue
        status = raw[:2].strip() or "?"
        path = raw[3:] if len(raw) > 3 else raw.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append({"status": status, "path": path.strip().strip('"')})
    return entries


def classify_path(path_text: str, size_bytes: int | None = None) -> str:
    normalized = path_text.replace("\\", "/")
    lower = normalized.lower()
    name = Path(normalized).name.lower()
    suffix = Path(normalized).suffix.lower()

    if (
        "__pycache__/" in lower
        or ".pytest_cache/" in lower
        or lower.startswith(".pytest_cache/")
        or suffix in {".pyc", ".pyo"}
        or lower.startswith("data/generated/test_pytest_tmp/")
        or lower.startswith("logs/")
        or lower.startswith("temp/")
        or lower.startswith("tmp/")
        or lower.startswith("data/source_cache/")
        or name.endswith(".log")
        or name.endswith(".tmp")
    ):
        return "should_ignore"
    if SECRETISH_PATTERN.search(normalized):
        return "do_not_commit"
    if size_bytes is not None and size_bytes > SIZE_REVIEW_BYTES:
        return "requires_user_review"
    if lower.endswith(".zip") or lower.endswith(".7z") or lower.endswith(".tar") or lower.endswith(".gz"):
        return "requires_user_review"
    if lower == "data/registry/mcp_registry_raw_v0_1.json" or lower.startswith("dist/"):
        return "requires_user_review"
    if lower == "public_ops/" or lower.startswith("public_ops/") or normalized in PACKAGE_8M_FILES:
        return "safe_package_8m_files"
    if lower in {"readme.md", "changelog.md", ".gitignore"} or lower.startswith("docs/"):
        return "safe_to_commit_later"
    if (
        lower.startswith("public_launch/")
        or lower.startswith("reports/")
        or lower.startswith("release/")
        or lower.startswith("github_upload/")
        or lower.startswith("deployment/")
    ):
        return "safe_to_commit_later"
    if lower.startswith("data/generated/") or lower.startswith("data/registry/") or lower.startswith("hf_upload/"):
        return "likely_generated_outputs"
    if lower.startswith(".github/issue_template/"):
        return "safe_to_commit_later"
    return "requires_user_review"


def classify_worktree(status_text: str, root: Path | None = None) -> dict[str, Any]:
    root = root or _repo_root()
    buckets: dict[str, list[dict[str, Any]]] = {
        "safe_package_8m_files": [],
        "likely_generated_outputs": [],
        "safe_to_commit_later": [],
        "should_ignore": [],
        "requires_user_review": [],
        "do_not_commit": [],
    }
    for entry in parse_status_paths(status_text):
        path = root / entry["path"]
        size = path.stat().st_size if path.exists() and path.is_file() else None
        bucket = classify_path(entry["path"], size)
        buckets[bucket].append({**entry, "size_bytes": size})
    return buckets


def _render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Worktree Classification",
        "",
        "This report classifies current working-tree changes. It does not delete files, run `git add .`, or commit generated leftovers automatically.",
        "",
        f"- Overall token: `{result['overall_token']}`",
        f"- Changed file entries: `{result['changed_entry_count']}`",
        "",
    ]
    for bucket, items in result["classifications"].items():
        lines.append(f"## {bucket}")
        if not items:
            lines.append("")
            lines.append("- None")
            lines.append("")
            continue
        for item in items:
            size = "" if item.get("size_bytes") is None else f" ({item['size_bytes']} bytes)"
            lines.append(f"- `{item['path']}` `{item['status']}`{size}")
        lines.append("")
    lines.extend(
        [
            "## Policy",
            "",
            "- Do not `git add .`.",
            "- Do not delete files from this report without explicit review.",
            "- Treat `do_not_commit` as blocking.",
            "- Treat raw payloads, dist archives, and large generated outputs as user-review items.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_worktree_hygiene_audit(
    status_text: str | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    status = {"ok": True, "stdout": status_text or "", "stderr": ""}
    diff = {"ok": True, "stdout": "", "stderr": ""}
    if status_text is None:
        status = _git(["status", "--short"], runner=runner)
        diff = _git(["diff", "--name-only"], runner=runner)
    classifications = classify_worktree(status["stdout"])
    do_not_commit_count = len(classifications["do_not_commit"])
    review_count = len(classifications["requires_user_review"])
    overall = "BLOCK" if do_not_commit_count else ("HOLD" if review_count else "PASS")
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "changed_entry_count": sum(len(items) for items in classifications.values()),
        "classifications": classifications,
        "git_status_ok": bool(status.get("ok")),
        "git_diff_name_only_ok": bool(diff.get("ok")),
        "git_diff_name_only": diff.get("stdout", ""),
        "warnings": [
            "No files were deleted.",
            "No broad staging was performed.",
            "Generated leftovers should be committed only after explicit review.",
        ],
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
        "deleted_files": [],
    }
    if write_result:
        _write_json(JSON_OUTPUT_PATH, result)
        _write(MD_OUTPUT_PATH, _render_markdown(result))
    return result


def main() -> None:
    result = run_worktree_hygiene_audit()
    print(
        "worktree_hygiene_audit: "
        f"{result['overall_token']} "
        f"entries={result['changed_entry_count']} "
        f"requires_user_review={len(result['classifications']['requires_user_review'])} "
        f"do_not_commit={len(result['classifications']['do_not_commit'])}"
    )


if __name__ == "__main__":
    main()
