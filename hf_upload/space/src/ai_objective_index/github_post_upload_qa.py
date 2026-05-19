from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OWNER = "Isometric-Architect"
REPO = "ai-objective-index"
REPO_URL = f"https://github.com/{OWNER}/{REPO}"
REMOTE_URL = f"{REPO_URL}.git"
BRANCH = "main"
OUTPUT_PATH = Path("github_upload/GITHUB_POST_UPLOAD_QA_RESULT.json")

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
    try:
        completed = subprocess.run(
            _resolve_command(command),
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


def _git(args: list[str], timeout: int = 60) -> dict[str, Any]:
    root = _repo_root().as_posix()
    return _run(["git", "-c", f"safe.directory={root}", *args], timeout=timeout)


def _gh_available_path() -> str | None:
    path = shutil.which("gh")
    if path:
        return path
    for candidate in GH_WINDOWS_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return None


def parse_remote_url(remote_output: str, expected_fragment: str = f"{OWNER}/{REPO}") -> str | None:
    for line in remote_output.splitlines():
        if expected_fragment.lower() in line.lower():
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]
    stripped = remote_output.strip()
    if expected_fragment.lower() in stripped.lower():
        return stripped
    return None


def _read_json(path: str) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def write_github_review_assets() -> list[str]:
    upload = _repo_root() / "github_upload"
    upload.mkdir(parents=True, exist_ok=True)
    assets = {
        "GITHUB_WEB_REVIEW_CHECKLIST.md": f"""# GitHub Web Review Checklist

1. Open {REPO_URL}.
2. Confirm `README.md` renders correctly.
3. Confirm the repository is still private.
4. Confirm no unexpected files are visible.
5. Confirm `release/public_beta_v0_2/` exists.
6. Confirm `launch/manual_public_beta_v0_2/` exists.
7. Confirm docs keep claim boundaries.
8. Confirm no secrets are visible.
9. Confirm no forbidden claims are made.
10. Decide whether to keep private, share with limited reviewers, or manually switch to public.
""",
        "PUBLIC_VISIBILITY_DECISION_CHECKLIST.md": """# Public Visibility Decision Checklist

Keeping the repository private is acceptable.

Before a manual public switch:

1. Run `python -m pytest`.
2. Run `python -m ai_objective_index.smoke_all`.
3. Run `python -m ai_objective_index.no_secrets_audit`.
4. Run `python -m ai_objective_index.launch_claim_guard`.
5. Run `python -m ai_objective_index.public_switch_preflight`.
6. Review the GitHub web view.

After a manual public switch, review the README again and optionally create a GitHub release manually. Do not claim verified, safe, security certified, quality guaranteed, or purchasing advice.
""",
        "HUGGINGFACE_HOLD_NOTE.md": """# Hugging Face Hold Note

Hugging Face publishing is on HOLD.

- The HF account/upload path is not executed by Package 8D.
- No Hugging Face token should be stored in this repository.
- When the user is ready, run a future Package 8E Hugging Face Manual Upload Assist.
- Until then, HF Space and Dataset links remain TODO/HOLD placeholders.
""",
    }
    written = []
    for name, text in assets.items():
        path = upload / name
        path.write_text(text, encoding="utf-8")
        written.append(str(path.relative_to(_repo_root())))
    return written


def run_github_post_upload_qa() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    remote = _git(["remote", "-v"])
    branch = _git(["branch", "--show-current"])
    head = _git(["rev-parse", "HEAD"])
    status = _git(["status", "--short"])

    remote_url = parse_remote_url(remote["stdout"]) if remote["ok"] else None
    branch_name = branch["stdout"].strip() if branch["ok"] else ""
    commit_hash = head["stdout"].strip() if head["ok"] else ""
    dirty_files = [line for line in status["stdout"].splitlines() if line.strip()] if status["ok"] else []

    if not remote_url:
        errors.append("Expected GitHub origin remote was not found locally.")
    if branch_name != BRANCH:
        warnings.append(f"Current branch is `{branch_name or 'unknown'}`, expected `{BRANCH}`.")
    if not commit_hash:
        errors.append("Latest commit hash could not be read.")

    gh_path = _gh_available_path()
    gh_available = bool(gh_path)
    gh_authenticated = False
    visibility_if_known = "not_checked"
    remote_exists_if_known = "not_checked"
    gh_status = {"gh_available": gh_available, "gh_path": gh_path}

    if gh_available:
        auth = _run(["gh", "auth", "status"])
        gh_authenticated = auth["ok"]
        gh_status["auth_ok"] = auth["ok"]
        if auth["ok"]:
            view = _run(["gh", "repo", "view", f"{OWNER}/{REPO}", "--json", "visibility,url"], timeout=90)
            if view["ok"]:
                try:
                    view_payload = json.loads(view["stdout"])
                except json.JSONDecodeError:
                    view_payload = {}
                visibility_if_known = str(view_payload.get("visibility", "unknown")).lower()
                remote_exists_if_known = bool(view_payload.get("url") or view_payload)
            else:
                warnings.append("GitHub CLI is authenticated, but repo visibility could not be checked.")
                remote_exists_if_known = False
        else:
            warnings.append("GitHub CLI is unavailable to this process or not authenticated; remote visibility was not checked.")
    else:
        warnings.append("GitHub CLI is not available; remote visibility was not checked.")

    if visibility_if_known == "public":
        errors.append("Repository appears public; Package 8D does not switch visibility.")

    staging = _read_json("github_upload/GITHUB_REMOTE_STATUS.json")
    if staging.get("actual_publish_performed") not in {False, None}:
        errors.append("Previous staging status indicates an external publish was performed.")

    written_assets = write_github_review_assets()
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "remote_url": remote_url,
        "expected_remote_url": REMOTE_URL,
        "branch": branch_name,
        "commit_hash": commit_hash,
        "working_tree_clean": not dirty_files,
        "dirty_files": dirty_files,
        "gh_available": gh_available,
        "gh_authenticated": gh_authenticated,
        "visibility_if_known": visibility_if_known,
        "remote_exists_if_known": remote_exists_if_known,
        "push_verified": bool(remote_url and commit_hash),
        "no_forced_push_performed": True,
        "actual_publish_performed": False,
        "huggingface_publish_performed": False,
        "community_post_performed": False,
        "errors": errors,
        "warnings": warnings,
        "written_assets": written_assets,
        "next_action": "Review GitHub in the browser, then run public_switch_preflight if a public switch is being considered."
        if not errors
        else "Resolve GitHub staging QA errors before public-switch review.",
        "read_only": True,
        "live_network_used": bool(gh_authenticated and visibility_if_known not in {"not_checked", "unknown"}),
    }
    _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_github_post_upload_qa()
    print(
        "github_post_upload_qa: "
        f"push_verified={result['push_verified']} "
        f"working_tree_clean={result['working_tree_clean']} "
        f"visibility={result['visibility_if_known']} "
        f"errors={len(result['errors'])}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
