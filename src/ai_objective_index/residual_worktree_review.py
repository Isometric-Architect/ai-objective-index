from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .worktree_hygiene_audit import parse_status_paths


OUTPUT_DIR = Path("public_ops") / "residual_review"
JSON_OUTPUT_PATH = OUTPUT_DIR / "RESIDUAL_WORKTREE_REVIEW_v0_1.json"
MD_OUTPUT_PATH = OUTPUT_DIR / "RESIDUAL_WORKTREE_REVIEW.md"
COMMIT_PLAN_PATH = OUTPUT_DIR / "RESIDUAL_COMMIT_PLAN.md"
IGNORE_PLAN_PATH = OUTPUT_DIR / "RESIDUAL_IGNORE_PLAN.md"
USER_REVIEW_PATH = OUTPUT_DIR / "RESIDUAL_USER_REVIEW_LIST.md"
SIZE_REVIEW_BYTES = 5 * 1024 * 1024

SENSITIVE_BASENAME = re.compile(
    r"^(?:\.env(?:\..*)?|credentials?(?:\..*)?|secrets?(?:\..*)?|tokens?(?:\..*)?|passwords?(?:\..*)?|private[_-]?key(?:\..*)?)$",
    re.IGNORECASE,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _read_json(path: str | Path) -> dict[str, Any]:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


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


def classify_residual_path(path_text: str, size_bytes: int | None = None) -> str:
    normalized = path_text.replace("\\", "/")
    lower = normalized.lower()
    name = Path(normalized).name
    lower_name = name.lower()

    if (
        "__pycache__/" in lower
        or ".pytest_cache/" in lower
        or lower.startswith(".pytest_cache/")
        or lower.endswith(".pyc")
        or lower.startswith("data/generated/test_pytest_tmp/")
        or lower.startswith("logs/")
        or lower.startswith("temp/")
        or lower.startswith("tmp/")
        or lower.startswith("data/source_cache/")
    ):
        return "safe_to_ignore"
    if SENSITIVE_BASENAME.match(lower_name) or lower.startswith("local_tokens/") or lower.startswith("local_credentials/"):
        return "possible_sensitive"
    if size_bytes is not None and size_bytes > SIZE_REVIEW_BYTES:
        return "possible_large_artifact"
    if lower.endswith((".zip", ".7z", ".tar", ".gz")) or lower.startswith("dist/"):
        return "possible_large_artifact"
    if lower == "data/registry/mcp_registry_raw_v0_1.json":
        return "requires_user_review"
    if (
        lower.startswith("data/generated/")
        or lower.startswith("data/registry/")
        or lower.startswith("hf_upload/")
        or lower.startswith("hf_dataset/")
        or lower.startswith("release/")
        or lower.startswith("launch/")
        or lower.startswith("deployment/")
    ):
        return "likely_generated_noise"
    if lower.startswith("public_ops/hf_parquet_converter_notification") or lower.startswith("public_ops/observation/") or lower.startswith("public_ops/residual_review/"):
        return "candidate_for_future_commit"
    if lower in {"readme.md", "changelog.md", ".gitignore"} or lower.startswith("docs/") or lower.startswith("tests/") or lower.startswith("src/"):
        return "candidate_for_future_commit"
    if lower.startswith("public_launch/") or lower.startswith(".github/issue_template/"):
        return "candidate_for_future_commit"
    return "unknown"


def classify_residual_status(status_text: str, root: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    root = root or _repo_root()
    buckets: dict[str, list[dict[str, Any]]] = {
        "safe_to_ignore": [],
        "candidate_for_future_commit": [],
        "requires_user_review": [],
        "likely_generated_noise": [],
        "possible_large_artifact": [],
        "possible_sensitive": [],
        "unknown": [],
    }
    for entry in parse_status_paths(status_text):
        full = root / entry["path"]
        size = full.stat().st_size if full.exists() and full.is_file() else None
        bucket = classify_residual_path(entry["path"], size)
        buckets[bucket].append({**entry, "size_bytes": size})
    return buckets


def _render_bucket(title: str, items: list[dict[str, Any]]) -> list[str]:
    lines = [f"## {title}", ""]
    if not items:
        lines.extend(["- None", ""])
        return lines
    for item in items:
        size = "" if item.get("size_bytes") is None else f" ({item['size_bytes']} bytes)"
        lines.append(f"- `{item['path']}` `{item['status']}`{size}")
    lines.append("")
    return lines


def render_review_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Residual Worktree Review",
        "",
        "This review classifies leftover working-tree changes after public launch operations. It does not delete files, stage everything, or commit generated leftovers.",
        "",
        f"- Overall token: `{result['overall_token']}`",
        f"- Changed entries: `{result['changed_entry_count']}`",
        f"- Possible sensitive entries: `{result['summary']['possible_sensitive']}`",
        "",
    ]
    for bucket, items in result["classifications"].items():
        lines.extend(_render_bucket(bucket, items))
    lines.extend(
        [
            "## Recommended Next Action",
            "",
            result["recommended_next_action"],
            "",
        ]
    )
    return "\n".join(lines)


def render_commit_plan(result: dict[str, Any]) -> str:
    lines = [
        "# Residual Commit Plan",
        "",
        "Do not commit all residual files at once. Candidate files should be grouped into future scoped packages.",
        "",
        "## Candidate For Future Commit",
        "",
    ]
    candidates = result["classifications"]["candidate_for_future_commit"]
    if not candidates:
        lines.append("- None")
    else:
        for item in candidates:
            lines.append(f"- `{item['path']}`")
    lines.extend(["", "## Current Recommendation", "", result["recommended_next_action"], ""])
    return "\n".join(lines)


def render_ignore_plan(result: dict[str, Any]) -> str:
    lines = [
        "# Residual Ignore Plan",
        "",
        "These entries look like cache or local transient files. Review before changing `.gitignore`; do not delete from this package.",
        "",
    ]
    ignored = result["classifications"]["safe_to_ignore"]
    if not ignored:
        lines.append("- None")
    else:
        for item in ignored:
            lines.append(f"- `{item['path']}`")
    lines.append("")
    return "\n".join(lines)


def render_user_review_list(result: dict[str, Any]) -> str:
    lines = [
        "# Residual User Review List",
        "",
        "Review these before any future commit, archive, or cleanup action.",
        "",
    ]
    review_items = (
        result["classifications"]["requires_user_review"]
        + result["classifications"]["possible_large_artifact"]
        + result["classifications"]["possible_sensitive"]
        + result["classifications"]["unknown"]
    )
    if not review_items:
        lines.append("- None")
    else:
        for item in review_items:
            lines.append(f"- `{item['path']}`")
    lines.append("")
    return "\n".join(lines)


def run_residual_worktree_review(
    status_text: str | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    status = {"ok": True, "stdout": status_text or "", "stderr": ""}
    if status_text is None:
        status = _git(["status", "--short"], runner=runner)
    classifications = classify_residual_status(status.get("stdout", ""))
    summary = {bucket: len(items) for bucket, items in classifications.items()}
    sensitive_count = summary["possible_sensitive"]
    overall = "BLOCK" if sensitive_count else ("HOLD_REVIEW" if sum(summary.values()) else "PASS")
    recommended = (
        "Clean possible sensitive entries before any launch action."
        if sensitive_count
        else "Observe public deployment first; defer residual cleanup to a scoped cleanup package."
        if sum(summary.values())
        else "No residual worktree entries detected."
    )
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "changed_entry_count": sum(summary.values()),
        "summary": summary,
        "classifications": classifications,
        "hygiene_input_available": bool(_read_json("public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json")),
        "recommended_next_action": recommended,
        "deleted_files": [],
        "git_add_all_used": False,
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(JSON_OUTPUT_PATH, result)
        _write(MD_OUTPUT_PATH, render_review_markdown(result))
        _write(COMMIT_PLAN_PATH, render_commit_plan(result))
        _write(IGNORE_PLAN_PATH, render_ignore_plan(result))
        _write(USER_REVIEW_PATH, render_user_review_list(result))
    return result


def main() -> None:
    result = run_residual_worktree_review()
    print(
        "residual_worktree_review: "
        f"{result['overall_token']} "
        f"entries={result['changed_entry_count']} "
        f"possible_sensitive={result['summary']['possible_sensitive']}"
    )


if __name__ == "__main__":
    main()
