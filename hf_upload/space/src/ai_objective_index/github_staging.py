from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .git_release_audit import build_manual_upload_commands, ensure_gitignore, run_git_release_audit


DEFAULT_OWNER = "Isometric-Architect"
DEFAULT_REPO = "ai-objective-index"
DEFAULT_BRANCH = "main"
UPLOAD_DIR = Path("github_upload")
GH_WINDOWS_CANDIDATES = [
    Path("C:/Program Files/GitHub CLI/gh.exe"),
    Path("C:/Program Files (x86)/GitHub CLI/gh.exe"),
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_command(command: list[str]) -> list[str]:
    if not command:
        return command
    if command[0] != "gh" or shutil.which("gh"):
        return command
    for candidate in GH_WINDOWS_CANDIDATES:
        if candidate.exists():
            return [str(candidate), *command[1:]]
    return command


def _run(command: list[str], timeout: int = 60) -> dict[str, Any]:
    resolved_command = _resolve_command(command)
    try:
        completed = subprocess.run(
            resolved_command,
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "ok": completed.returncode == 0,
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "returncode": None, "stdout": "", "stderr": str(exc), "ok": False}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def detect_gh_status() -> dict[str, Any]:
    gh_path = shutil.which("gh")
    if not gh_path:
        gh_path = next((str(path) for path in GH_WINDOWS_CANDIDATES if path.exists()), None)
    if not gh_path:
        return {
            "gh_available": False,
            "gh_authenticated": False,
            "message": "GitHub CLI is not installed or not on PATH.",
        }
    version = _run(["gh", "--version"])
    auth = _run(["gh", "auth", "status"])
    return {
        "gh_available": True,
        "gh_authenticated": bool(auth["ok"]),
        "gh_path": gh_path,
        "version_stdout": version["stdout"],
        "auth_stdout": auth["stdout"],
        "auth_stderr": auth["stderr"],
    }


def detect_git_status() -> dict[str, Any]:
    inside = _run(["git", "rev-parse", "--is-inside-work-tree"])
    branch = _run(["git", "branch", "--show-current"]) if inside["ok"] else {"stdout": "", "ok": False}
    remote = _run(["git", "remote", "-v"]) if inside["ok"] else {"stdout": "", "ok": False}
    status = _run(["git", "status", "--short", "--branch"]) if inside["ok"] else {"stdout": "", "ok": False}
    return {
        "git_repository": inside["ok"] and inside["stdout"].strip() == "true",
        "branch": branch["stdout"].strip(),
        "remote_v": remote["stdout"],
        "status": status["stdout"],
    }


def _audit_outputs_ok() -> dict[str, Any]:
    root = _repo_root()
    checks: dict[str, Any] = {}
    for rel, key in [
        ("data/generated/no_secrets_audit_result_v0_2.json", "no_secrets"),
        ("data/generated/launch_claim_guard_result_v0_2.json", "launch_claim_guard"),
        ("data/generated/final_preflight_result_v0_2.json", "final_preflight"),
        ("data/generated/smoke_all_result_v0_1.json", "smoke_all"),
    ]:
        path = root / rel
        if not path.exists():
            checks[key] = {"exists": False, "ok": False}
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            checks[key] = {"exists": True, "ok": False}
            continue
        if key == "no_secrets":
            ok = int(payload.get("finding_count", 1) or 0) == 0
        elif key == "launch_claim_guard":
            ok = payload.get("overall_token") == "PASS"
        elif key == "final_preflight":
            ok = payload.get("overall_token") == "PASS"
        else:
            ok = payload.get("pass") is True
        checks[key] = {"exists": True, "ok": ok}
    return {
        "checks": checks,
        "ok": all(item["ok"] for item in checks.values()),
    }


def _write_upload_docs(result: dict[str, Any]) -> None:
    upload_dir = _repo_root() / UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    owner = result["owner"]
    repo = result["repo"]
    visibility = result["visibility"]
    _write(
        upload_dir / "GITHUB_UPLOAD_COMMANDS.md",
        build_manual_upload_commands(owner=owner, repo=repo, visibility=visibility),
    )
    _write_json(upload_dir / "GITHUB_REMOTE_STATUS.json", result)
    _write(
        upload_dir / "GITHUB_STAGING_SUMMARY.md",
        f"""# GitHub Staging Summary

- Owner: `{owner}`
- Repository: `{repo}`
- Visibility requested: `{visibility}`
- Branch: `{result['branch']}`
- GitHub CLI available: `{str(result['gh_status'].get('gh_available')).lower()}`
- GitHub CLI authenticated: `{str(result['gh_status'].get('gh_authenticated')).lower()}`
- Repository created: `{str(result['repo_created']).lower()}`
- Push performed: `{str(result['actual_push_performed']).lower()}`
- Actual publish performed: `{str(result['actual_publish_performed']).lower()}`

AOI remains a read-only MCP/API benchmark. `public_beta_mcp` contains registry metadata candidates, not verified or security certified tools.
""",
    )
    _write(
        upload_dir / "POST_UPLOAD_CHECKLIST.md",
        """# Post Upload Checklist

1. Open the GitHub repository.
2. Review `README.md`.
3. Review `release/public_beta_v0_2/`.
4. Confirm no secrets are visible.
5. Confirm claim boundaries say not verified, not security certified, not a quality guarantee, and not purchasing advice.
6. Decide whether to make the repository public later.
7. Create a GitHub release manually if desired.
""",
    )


def prepare_github_staging(
    owner: str = DEFAULT_OWNER,
    repo: str = DEFAULT_REPO,
    visibility: str | None = None,
    branch: str = DEFAULT_BRANCH,
    allow_push: bool = True,
) -> dict[str, Any]:
    visibility = visibility or os.environ.get("AOI_GITHUB_VISIBILITY", "private")
    if visibility not in {"private", "public"}:
        visibility = "private"

    ensure_gitignore()
    release_audit = run_git_release_audit()
    audit_status = _audit_outputs_ok()
    gh_status = detect_gh_status()
    git_status = detect_git_status()

    result: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "owner": owner,
        "repo": repo,
        "visibility": visibility,
        "branch": branch,
        "release_audit": release_audit,
        "pre_upload_audits": audit_status,
        "gh_status": gh_status,
        "git_status_before": git_status,
        "repo_created": False,
        "actual_push_performed": False,
        "actual_publish_performed": False,
        "remote_url": None,
        "commit_hash": None,
        "errors": [],
        "warnings": [],
        "next_action": "",
        "read_only": True,
        "live_network_used": False,
    }

    if not audit_status["ok"]:
        result["errors"].append("Pre-upload audit outputs are missing or not passing.")
        result["next_action"] = "Run pytest, no_secrets_audit, launch_claim_guard, smoke_all, and final_preflight before pushing."
        _write_upload_docs(result)
        return result

    if not gh_status.get("gh_available"):
        result["warnings"].append("GitHub CLI is unavailable; no push attempted.")
        result["next_action"] = "Install GitHub CLI or create a repository in the browser, then use GITHUB_UPLOAD_COMMANDS.md."
        _write_upload_docs(result)
        return result

    if not gh_status.get("gh_authenticated"):
        result["warnings"].append("GitHub CLI is not authenticated; no push attempted.")
        result["next_action"] = "Run gh auth login manually. Do not paste tokens into the repository."
        _write_upload_docs(result)
        return result

    if not allow_push:
        result["warnings"].append("allow_push=False; no push attempted.")
        result["next_action"] = "Review GITHUB_UPLOAD_COMMANDS.md."
        _write_upload_docs(result)
        return result

    if not git_status["git_repository"]:
        init = _run(["git", "init"])
        branch_cmd = _run(["git", "branch", "-M", branch])
        if not init["ok"] or not branch_cmd["ok"]:
            result["errors"].append("Could not initialize local git repository.")
            result["next_action"] = "Initialize git manually and review errors."
            _write_upload_docs(result)
            return result

    _run(["git", "config", "user.name", owner])
    _run(["git", "config", "user.email", "artradarwon@gmail.com"])
    add = _run(["git", "add", "."])
    if not add["ok"]:
        result["errors"].append(f"git add failed: {add['stderr']}")
        result["next_action"] = "Review ignored files and git add errors."
        _write_upload_docs(result)
        return result

    commit = _run(
        [
            "git",
            "commit",
            "-m",
            "Initial AI Objective Index public beta candidate",
            "-m",
            "Read-only MCP/API benchmark engine with public_beta_mcp registry metadata candidates. Not verified, not security certified, not a quality guarantee, and no payment/booking/login/email/purchase/contract execution.",
        ]
    )
    if not commit["ok"] and "nothing to commit" not in (commit["stdout"] + commit["stderr"]).lower():
        result["errors"].append(f"git commit failed: {commit['stderr']}")
        result["next_action"] = "Review git commit errors."
        _write_upload_docs(result)
        return result

    head = _run(["git", "rev-parse", "HEAD"])
    result["commit_hash"] = head["stdout"] if head["ok"] else None
    current_remote = _run(["git", "remote", "get-url", "origin"])
    expected_remote_fragment = f"{owner}/{repo}"

    if current_remote["ok"]:
        result["remote_url"] = current_remote["stdout"]
        if expected_remote_fragment.lower() not in current_remote["stdout"].lower():
            result["errors"].append("Existing origin remote differs from requested owner/repo. No push attempted.")
            result["next_action"] = "Review git remote -v and choose the correct repository."
            _write_upload_docs(result)
            return result
        push = _run(["git", "push", "-u", "origin", branch], timeout=180)
        result["actual_push_performed"] = push["ok"]
        result["errors"].extend([] if push["ok"] else [push["stderr"]])
    else:
        visibility_flag = "--public" if visibility == "public" else "--private"
        create = _run(
            [
                "gh",
                "repo",
                "create",
                f"{owner}/{repo}",
                visibility_flag,
                "--source=.",
                "--remote=origin",
                "--push",
            ],
            timeout=240,
        )
        result["repo_created"] = create["ok"]
        result["actual_push_performed"] = create["ok"]
        if create["ok"]:
            remote = _run(["git", "remote", "get-url", "origin"])
            result["remote_url"] = remote["stdout"] if remote["ok"] else None
        else:
            result["errors"].append(create["stderr"] or create["stdout"] or "gh repo create failed.")

    result["git_status_after"] = detect_git_status()
    result["next_action"] = (
        "Open the GitHub repository and review README/release assets."
        if result["actual_push_performed"]
        else "No push was performed. Review GITHUB_UPLOAD_COMMANDS.md and errors."
    )
    _write_upload_docs(result)
    return result


def main() -> None:
    result = prepare_github_staging()
    print(
        "github_staging: "
        f"gh_available={result['gh_status'].get('gh_available')} "
        f"gh_authenticated={result['gh_status'].get('gh_authenticated')} "
        f"repo_created={result['repo_created']} "
        f"push_performed={result['actual_push_performed']} "
        f"visibility={result['visibility']}"
    )
    if result["errors"]:
        print(f"errors={len(result['errors'])}")
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
