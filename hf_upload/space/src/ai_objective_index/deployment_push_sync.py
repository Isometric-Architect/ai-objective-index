from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .deployment_link_sync import OUTPUT_DIR
from .hf_github_crosslink_audit import audit_crosslinks
from .launch_claim_guard import run_launch_claim_guard, save_launch_claim_guard
from .no_secrets_audit import run_no_secrets_audit, save_no_secrets_audit
from .private_deployment_qa import run_private_deployment_qa
from .smoke_all import run_smoke_all


OUTPUT_PATH = OUTPUT_DIR / "PUSH_SYNC_RESULT.json"
COMMIT_MESSAGE = "Package 8H: private deployment sync and Hugging Face link binding"

SAFE_STAGE_PATHS = [
    "README.md",
    "CHANGELOG.md",
    "docs",
    "src/ai_objective_index/deployment_link_sync.py",
    "src/ai_objective_index/private_deployment_qa.py",
    "src/ai_objective_index/hf_github_crosslink_audit.py",
    "src/ai_objective_index/deployment_push_sync.py",
    "src/ai_objective_index/hf_auth_check.py",
    "src/ai_objective_index/hf_private_upload.py",
    "src/ai_objective_index/hf_post_upload_qa.py",
    "src/ai_objective_index/hf_upload_packager.py",
    "src/ai_objective_index/hf_upload_audit.py",
    "tests/test_deployment_link_sync.py",
    "tests/test_private_deployment_qa.py",
    "tests/test_hf_github_crosslink_audit.py",
    "tests/test_deployment_push_sync.py",
    "tests/test_private_deployment_assets.py",
    "tests/test_hf_auth_check.py",
    "tests/test_hf_private_upload.py",
    "tests/test_hf_post_upload_qa.py",
    "tests/test_hf_upload_docs.py",
    "hf_upload",
    "huggingface_upload",
    "deployment/private_deployment_v0_2",
    "github_upload/HUGGINGFACE_HOLD_NOTE.md",
    "launch/manual_public_beta_v0_2/FINAL_LINKS_PLACEHOLDER.md",
    "launch/manual_public_beta_v0_2/README_LAUNCH_STEPS.md",
    "launch/manual_public_beta_v0_2/GITHUB_RELEASE_DRAFT.md",
    "release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md",
    "hf_dataset/README.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _run(command: list[str], timeout: int = 120) -> dict[str, Any]:
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
            "stdout": (completed.stdout or "").strip(),
            "stderr": (completed.stderr or "").strip(),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}


def _git(args: list[str], timeout: int = 120, runner: Callable[[list[str], int], dict[str, Any]] = _run) -> dict[str, Any]:
    root = _repo_root().as_posix()
    return runner(["git", "-c", f"safe.directory={root}", *args], timeout)


def _safe_existing_paths(paths: list[str] | None = None) -> list[str]:
    root = _repo_root()
    safe: list[str] = []
    for item in paths or SAFE_STAGE_PATHS:
        if (root / item).exists():
            safe.append(item)
    return safe


def _command_has_force(command: list[str]) -> bool:
    return any(part in {"--force", "-f", "--force-with-lease"} for part in command)


def _minimum_checks() -> tuple[bool, list[str], dict[str, Any]]:
    errors: list[str] = []
    no_secrets = run_no_secrets_audit()
    save_no_secrets_audit(no_secrets)
    launch_claim = run_launch_claim_guard()
    save_launch_claim_guard(launch_claim)
    smoke = run_smoke_all()
    deployment_qa = run_private_deployment_qa()
    crosslink = audit_crosslinks()

    if int(no_secrets.get("finding_count", 1) or 0) > 0:
        errors.append("no_secrets_audit found blocking findings.")
    if launch_claim.get("overall_token") != "PASS":
        errors.append("launch_claim_guard did not pass.")
    if smoke.get("pass") is not True:
        errors.append("smoke_all did not pass.")
    if deployment_qa.get("overall_token") not in {"PASS", "HOLD"}:
        errors.append("private_deployment_qa blocked.")
    if crosslink.get("overall_token") != "PASS":
        errors.append("hf_github_crosslink_audit did not pass.")
    return not errors, errors, {
        "no_secrets": no_secrets.get("overall_token"),
        "launch_claim_guard": launch_claim.get("overall_token"),
        "smoke_all": smoke.get("pass"),
        "private_deployment_qa": deployment_qa.get("overall_token"),
        "crosslink_audit": crosslink.get("overall_token"),
    }


def run_deployment_push_sync(
    execute: bool = False,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    stage_paths: list[str] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    safe_paths = _safe_existing_paths(stage_paths)
    status = _git(["status", "--short"], runner=runner)
    branch = _git(["branch", "--show-current"], runner=runner)
    remote = _git(["remote", "get-url", "origin"], runner=runner)

    result: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "would_stage": safe_paths,
        "status_short": status.get("stdout", ""),
        "committed": False,
        "pushed": False,
        "commit_hash": None,
        "branch": (branch.get("stdout") or "main").strip() or "main",
        "remote_url": remote.get("stdout") or "",
        "working_tree_clean_after": False,
        "visibility_changed": False,
        "force_push_used": False,
        "errors": errors,
        "warnings": warnings,
        "checks": {},
        "actual_publish_performed": False,
        "read_only": True,
        "live_network_used": False,
    }

    if not execute:
        result["next_action"] = "Dry run complete. Review would_stage, then run --execute if private push is desired."
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    checks_ok, check_errors, check_summary = _minimum_checks()
    result["checks"] = check_summary
    if not checks_ok:
        result["errors"].extend(check_errors)
        result["next_action"] = "Resolve local audit errors before push."
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    for path in safe_paths:
        add_command = ["add", "--", path]
        if _command_has_force(add_command):
            result["errors"].append("Unsafe git add command generated.")
            break
        add = _git(add_command, runner=runner)
        if not add.get("ok"):
            result["errors"].append(f"git add failed for {path}: {add.get('stderr')}")
            break

    if result["errors"]:
        result["next_action"] = "Resolve staging errors before commit."
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    diff = _git(["diff", "--cached", "--quiet"], runner=runner)
    if diff.get("returncode") == 0:
        warnings.append("No staged changes to commit.")
    else:
        commit = _git(["commit", "-m", COMMIT_MESSAGE], timeout=180, runner=runner)
        if not commit.get("ok"):
            result["errors"].append(f"git commit failed: {commit.get('stderr')}")
        else:
            result["committed"] = True
            head = _git(["rev-parse", "HEAD"], runner=runner)
            result["commit_hash"] = head.get("stdout")

    if not result["errors"]:
        push_command = ["push", "-u", "origin", result["branch"]]
        if _command_has_force(push_command):
            result["errors"].append("Force push command refused.")
            result["force_push_used"] = True
        else:
            push = _git(push_command, timeout=240, runner=runner)
            if not push.get("ok"):
                result["errors"].append(f"git push failed: {push.get('stderr')}")
            else:
                result["pushed"] = True
                result["live_network_used"] = True

    final_status = _git(["status", "--short"], runner=runner)
    result["working_tree_clean_after"] = not bool(final_status.get("stdout", "").strip())
    result["next_action"] = (
        "Private GitHub sync pushed. Review GitHub and Hugging Face links in the browser."
        if result["pushed"] and not result["errors"]
        else "Review PUSH_SYNC_RESULT errors/warnings."
    )
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Private deployment GitHub push sync.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_deployment_push_sync(execute=bool(args.execute) and not bool(args.dry_run))
    print(
        "deployment_push_sync: "
        f"dry_run={result['dry_run']} "
        f"committed={result['committed']} "
        f"pushed={result['pushed']} "
        f"errors={len(result['errors'])}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
