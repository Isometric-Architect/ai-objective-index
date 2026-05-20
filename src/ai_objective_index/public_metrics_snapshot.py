from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope


OBSERVATION_DIR = Path("public_ops") / "observation"
SNAPSHOT_0H_PATH = OBSERVATION_DIR / "OBSERVATION_SNAPSHOT_0H.json"
SNAPSHOT_0H_MD_PATH = OBSERVATION_DIR / "PUBLIC_METRICS_SNAPSHOT_0H.md"


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


def _run(command: list[str], timeout: int = 30) -> dict[str, Any]:
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
    return runner(["git", "-c", f"safe.directory={_repo_root().as_posix()}", *args], 30)


def _count_jsonl_lines(path: str | Path) -> int:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return 0
    count = 0
    with full.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def _parse_json_stdout(result: dict[str, Any]) -> dict[str, Any]:
    if not result.get("ok"):
        return {}
    try:
        payload = json.loads(result.get("stdout", "") or "{}")
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def collect_github_metrics(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    allow_gh_checks: bool = True,
) -> dict[str, Any]:
    latest_commit = _git(["rev-parse", "--short", "HEAD"], runner=runner)
    metrics: dict[str, Any] = {
        "repo_url": GITHUB_URL,
        "latest_commit": latest_commit.get("stdout", "").strip() if latest_commit.get("ok") else "not_checked",
        "stars_count": "not_checked",
        "open_issues_count": "not_checked",
        "visibility": "not_checked",
        "gh_available": False,
        "gh_checked": False,
    }
    if not allow_gh_checks:
        return metrics
    gh_version = runner(["gh", "--version"], 15)
    metrics["gh_available"] = bool(gh_version.get("ok"))
    if not gh_version.get("ok"):
        return metrics

    repo_view = runner(
        [
            "gh",
            "repo",
            "view",
            "Isometric-Architect/ai-objective-index",
            "--json",
            "stargazerCount,visibility",
        ],
        30,
    )
    repo_payload = _parse_json_stdout(repo_view)
    if repo_payload:
        metrics["stars_count"] = repo_payload.get("stargazerCount", "not_checked")
        metrics["visibility"] = repo_payload.get("visibility", "not_checked")
        metrics["gh_checked"] = True

    issues = runner(
        ["gh", "issue", "list", "--repo", "Isometric-Architect/ai-objective-index", "--state", "open", "--limit", "100", "--json", "number"],
        30,
    )
    if issues.get("ok"):
        try:
            issue_payload = json.loads(issues.get("stdout", "") or "[]")
        except json.JSONDecodeError:
            issue_payload = []
        if isinstance(issue_payload, list):
            metrics["open_issues_count"] = len(issue_payload)
            metrics["gh_checked"] = True
    return metrics


def collect_hf_metrics() -> dict[str, Any]:
    post_upload = _read_json("huggingface_upload/HF_POST_UPLOAD_QA_RESULT.json")
    metrics: dict[str, Any] = {
        "space_url": HF_SPACE_URL,
        "dataset_url": HF_DATASET_URL,
        "space_status": post_upload.get("build_status_if_available") or post_upload.get("space_status") or "not_checked",
        "dataset_exists": post_upload.get("dataset_exists_if_checked", "not_checked"),
        "source": "local_post_upload_qa" if post_upload else "not_checked",
    }
    return metrics


def render_metrics_markdown(snapshot: dict[str, Any]) -> str:
    github = snapshot["github"]
    hf = snapshot["huggingface"]
    lines = [
        "# Public Metrics Snapshot 0H",
        "",
        f"- Generated at: `{snapshot['generated_at']}`",
        f"- GitHub: {github['repo_url']}",
        f"- GitHub stars: `{github['stars_count']}`",
        f"- GitHub open issues: `{github['open_issues_count']}`",
        f"- GitHub latest commit: `{github['latest_commit']}`",
        f"- Hugging Face Space: {hf['space_url']}",
        f"- Hugging Face Space status: `{hf['space_status']}`",
        f"- Hugging Face Dataset: {hf['dataset_url']}",
        f"- Hugging Face Dataset exists: `{hf['dataset_exists']}`",
        f"- public_beta_mcp count: `{snapshot['public_beta_mcp_count']}`",
        f"- registry source trace count: `{snapshot['source_trace_count']}`",
        "",
        "## Launch Boundaries",
        "",
        "- Community post performed: `false`",
        "- GitHub Release created: `false`",
        "- MCP Registry submission performed: `false`",
        "- This snapshot is not a quality guarantee, verification, certification, or purchasing advice.",
    ]
    return "\n".join(lines) + "\n"


def run_public_metrics_snapshot(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
    allow_gh_checks: bool = True,
) -> dict[str, Any]:
    public_beta_mcp_count = len(get_store_for_scope("public_beta_mcp").list_objects())
    source_trace_count = _count_jsonl_lines("data/registry/mcp_registry_source_traces_v0_1.jsonl")
    snapshot = {
        "generated_at": datetime.now(UTC).isoformat(),
        "phase": "0h",
        "github": collect_github_metrics(runner=runner, allow_gh_checks=allow_gh_checks),
        "huggingface": collect_hf_metrics(),
        "public_beta_mcp_count": public_beta_mcp_count,
        "source_trace_count": source_trace_count,
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "read_only": True,
        "token_printed": False,
        "actual_publish_performed": False,
        "notes": [
            "Online/API checks may be not_checked when unavailable; that is not a failure.",
            "No community post, GitHub Release, or MCP Registry submission was performed.",
        ],
    }
    if write_result:
        _write_json(SNAPSHOT_0H_PATH, snapshot)
        _write(SNAPSHOT_0H_MD_PATH, render_metrics_markdown(snapshot))
    return snapshot


def main() -> None:
    snapshot = run_public_metrics_snapshot()
    print(
        "public_metrics_snapshot: "
        f"phase={snapshot['phase']} "
        f"public_beta_mcp={snapshot['public_beta_mcp_count']} "
        f"github_stars={snapshot['github']['stars_count']} "
        f"issues={snapshot['github']['open_issues_count']}"
    )


if __name__ == "__main__":
    main()
