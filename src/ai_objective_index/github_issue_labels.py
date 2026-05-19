from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .deployment_link_sync import GITHUB_URL
from .public_ops_baseline import OUTPUT_DIR


PLAN_PATH = OUTPUT_DIR / "GITHUB_ISSUE_LABELS_PLAN.md"
RESULT_PATH = OUTPUT_DIR / "GITHUB_ISSUE_LABELS_RESULT.json"
REPO = "Isometric-Architect/ai-objective-index"

LABELS = [
    {"name": "public-beta", "color": "0E8A16", "description": "Public beta feedback and triage."},
    {"name": "failed-query", "color": "D93F0B", "description": "A query produced weak, missing, or surprising results."},
    {"name": "wrong-field", "color": "B60205", "description": "A field appears incorrect or unsupported."},
    {"name": "scoring-dispute", "color": "FBCA04", "description": "Ranking or score component dispute."},
    {"name": "missing-source-trace", "color": "5319E7", "description": "A result needs better source trace coverage."},
    {"name": "install-failure", "color": "C5DEF5", "description": "Local API, MCP, or demo setup issue."},
    {"name": "docs-confusion", "color": "006B75", "description": "Documentation is confusing or incomplete."},
    {"name": "add-tool", "color": "1D76DB", "description": "Suggestion for a new tool/API/SaaS/MCP object."},
    {"name": "good-first-feedback", "color": "7057FF", "description": "Small, actionable public beta feedback item."},
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _sanitize(text: Any) -> str:
    value = str(text or "")
    for marker in ["gho_", "ghp_", "github_pat_", "hf_", "bearer "]:
        index = value.lower().find(marker.lower())
        if index >= 0:
            value = value[:index] + "[redacted]"
            break
    return value[:500]


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
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def write_labels_plan(labels: list[dict[str, str]] | None = None) -> Path:
    labels = labels or LABELS
    lines = [
        "# GitHub Issue Labels Plan",
        "",
        f"Repository: {GITHUB_URL}",
        "",
        "Dry-run is the default. Execute mode creates or updates labels with GitHub CLI if authenticated.",
        "",
    ]
    for label in labels:
        lines.append(f"- `{label['name']}`: {label['description']} color `#{label['color']}`")
    lines.extend(
        [
            "",
            "No labels are deleted. No tokens are printed or requested.",
        ]
    )
    return _write(PLAN_PATH, "\n".join(lines) + "\n")


def _gh_available() -> bool:
    return bool(shutil.which("gh"))


def _gh_authenticated(runner: Callable[[list[str], int], dict[str, Any]]) -> bool:
    result = runner(["gh", "auth", "status"], 60)
    return bool(result.get("ok"))


def _create_or_update_label(
    label: dict[str, str],
    runner: Callable[[list[str], int], dict[str, Any]],
) -> dict[str, Any]:
    create = runner(
        [
            "gh",
            "label",
            "create",
            label["name"],
            "--repo",
            REPO,
            "--color",
            label["color"],
            "--description",
            label["description"],
        ],
        60,
    )
    if create.get("ok"):
        return {"label": label["name"], "status": "created", "ok": True}
    combined = f"{create.get('stdout', '')}\n{create.get('stderr', '')}".lower()
    if "already exists" in combined or "name already exists" in combined:
        edit = runner(
            [
                "gh",
                "label",
                "edit",
                label["name"],
                "--repo",
                REPO,
                "--color",
                label["color"],
                "--description",
                label["description"],
            ],
            60,
        )
        return {"label": label["name"], "status": "existing_updated" if edit.get("ok") else "existing_update_failed", "ok": bool(edit.get("ok")), "error": edit.get("stderr")}
    return {"label": label["name"], "status": "failed", "ok": False, "error": create.get("stderr") or create.get("stdout")}


def run_github_issue_labels(
    execute: bool = False,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    plan_path = write_labels_plan()
    gh_available = _gh_available()
    gh_authenticated = _gh_authenticated(runner) if execute and gh_available else False
    labels_result: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    if execute:
        if not gh_available:
            warnings.append("GitHub CLI is unavailable; write labels manually from the plan.")
        elif not gh_authenticated:
            warnings.append("GitHub CLI is not authenticated; run gh auth login locally if label creation is desired.")
        else:
            for label in LABELS:
                item = _create_or_update_label(label, runner)
                labels_result.append(item)
                if not item.get("ok"):
                    errors.append(f"{item['label']}: {item.get('error')}")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "labels_planned": [label["name"] for label in LABELS],
        "labels_created_or_existing": labels_result,
        "plan_path": str(plan_path),
        "gh_available": gh_available,
        "gh_authenticated": gh_authenticated,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
        "read_only": True,
        "live_network_used": bool(execute and gh_authenticated),
        "actual_publish_performed": False,
        "community_post_performed": False,
    }
    if write_result:
        _write_json(RESULT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Prepare or create GitHub issue labels.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_github_issue_labels(execute=bool(args.execute) and not bool(args.dry_run))
    print(
        "github_issue_labels: "
        f"dry_run={result['dry_run']} "
        f"execute={result['execute']} "
        f"labels={len(result['labels_planned'])} "
        f"errors={len(result['errors'])}"
    )


if __name__ == "__main__":
    main()
