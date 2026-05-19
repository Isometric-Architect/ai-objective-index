from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .final_public_dry_run import run_final_public_dry_run
from .launch_claim_guard import run_launch_claim_guard, save_launch_claim_guard
from .no_contact_launch_gate import run_no_contact_launch_gate
from .no_secrets_audit import run_no_secrets_audit, save_no_secrets_audit
from .public_beta_message_guard import run_public_beta_message_guard
from .public_launch_gate import OUTPUT_DIR
from .smoke_all import run_smoke_all


OUTPUT_PATH = OUTPUT_DIR / "PREPUBLIC_SYNC_RESULT.json"
COMMIT_MESSAGE = "Package 8J: pre-public sync and final public dry-run"

SAFE_STAGE_PATHS = [
    "README.md",
    "CHANGELOG.md",
    "docs/community_launch.md",
    "docs/manual_publish_checklist.md",
    "docs/public_beta_release_plan.md",
    "docs/launch_notes.md",
    "docs/no_contact_public_beta_strategy.md",
    "docs/ai_reviewer_simulation.md",
    "docs/issue_based_feedback_loop.md",
    "docs/package_8i_public_launch_decision_gate.md",
    "docs/public_launch_policy.md",
    "docs/private_reviewer_workflow.md",
    "docs/token_revocation_after_upload.md",
    "docs/package_8j_prepublic_sync.md",
    "docs/final_public_dry_run.md",
    "src/ai_objective_index/public_launch_gate.py",
    "src/ai_objective_index/public_visibility_switch.py",
    "src/ai_objective_index/public_launch_claim_audit.py",
    "src/ai_objective_index/private_reviewer_packager.py",
    "src/ai_objective_index/token_revocation_checklist.py",
    "src/ai_objective_index/ai_reviewer_simulation.py",
    "src/ai_objective_index/issue_feedback_loop_packager.py",
    "src/ai_objective_index/public_beta_message_guard.py",
    "src/ai_objective_index/no_contact_launch_gate.py",
    "src/ai_objective_index/prepublic_sync.py",
    "src/ai_objective_index/final_public_dry_run.py",
    "src/ai_objective_index/prepublic_state_report.py",
    "tests/test_ai_reviewer_simulation.py",
    "tests/test_issue_feedback_loop_packager.py",
    "tests/test_public_beta_message_guard.py",
    "tests/test_no_contact_launch_gate.py",
    "tests/test_no_contact_public_beta_assets.py",
    "tests/test_public_launch_gate.py",
    "tests/test_public_visibility_switch.py",
    "tests/test_public_launch_claim_audit.py",
    "tests/test_private_reviewer_packager.py",
    "tests/test_token_revocation_checklist.py",
    "tests/test_public_launch_assets.py",
    "tests/test_prepublic_sync.py",
    "tests/test_final_public_dry_run.py",
    "tests/test_prepublic_state_report.py",
    "tests/test_prepublic_assets.py",
    "public_launch/PUBLIC_LAUNCH_GATE_RESULT.json",
    "public_launch/PUBLIC_VISIBILITY_SWITCH_DRY_RUN.json",
    "public_launch/PUBLIC_VISIBILITY_SWITCH_RESULT.json",
    "public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json",
    "public_launch/PUBLIC_LAUNCH_README_CHECKLIST.md",
    "public_launch/PUBLIC_ANNOUNCEMENT_DRAFTS.md",
    "public_launch/PRIVATE_REVIEWER_INVITE_DRAFT.md",
    "public_launch/TOKEN_REVOCATION_CHECKLIST.md",
    "public_launch/GO_NO_GO_DECISION.md",
    "public_launch/AI_REVIEWER_SIMULATION_RESULT.json",
    "public_launch/NO_CONTACT_LAUNCH_GATE_RESULT.json",
    "public_launch/ISSUE_FEEDBACK_LOOP_PLAN.md",
    "public_launch/PUBLIC_BETA_MESSAGE_GUARD_RESULT.json",
    "public_launch/NO_CONTACT_GO_NO_GO_DECISION.md",
    "public_launch/PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md",
    "public_launch/PREPUBLIC_SYNC_RESULT.json",
    "public_launch/FINAL_PUBLIC_DRY_RUN_RESULT.json",
    "public_launch/PREPUBLIC_STATE_REPORT.json",
    "public_launch/FINAL_PUBLIC_SWITCH_INSTRUCTIONS.md",
    "public_launch/PREPUBLIC_REVIEW_CHECKLIST.md",
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
    return [item for item in paths or SAFE_STAGE_PATHS if (root / item).exists()]


def _command_has_force(command: list[str]) -> bool:
    return any(part in {"--force", "-f", "--force-with-lease"} for part in command)


def write_prepublic_assets() -> list[str]:
    switch = """# Final Public Switch Instructions

Package 8J does not make anything public.

## A. Codex-Assisted Public Switch Later

Only after the user explicitly says to proceed:

1. Set `AOI_PUBLIC_LAUNCH_CONFIRM=YES`.
2. Run:

```powershell
python -m ai_objective_index.public_launch_execute --execute
```

Then run:

```powershell
python -m ai_objective_index.public_url_qa
python -m ai_objective_index.post_public_state_report
```

## B. Manual Public Switch

GitHub:

1. Open repository settings.
2. Go to Danger Zone.
3. Change visibility to Public.

Hugging Face Space:

1. Open Space settings.
2. Change Visibility to Public.

Hugging Face Dataset:

1. Open Dataset settings.
2. Change Visibility to Public.

## Warnings

- Do not claim verified MCP servers.
- Do not claim safe servers, security certification, quality guarantee, or production readiness.
- Do not post community announcements until links are public and checked.
"""
    checklist = """# Pre-Public Review Checklist

- [ ] GitHub README renders.
- [ ] Hugging Face Space runs.
- [ ] Sample query works.
- [ ] Dataset files are visible.
- [ ] No token or secret is present.
- [ ] No forbidden claims are present.
- [ ] `public_beta_mcp=50` or latest expected count is confirmed.
- [ ] Issue templates are available.
- [ ] No-contact post draft is conservative.
- [ ] Public switch decision is recorded by the human owner.
"""
    paths = [
        _write(OUTPUT_DIR / "FINAL_PUBLIC_SWITCH_INSTRUCTIONS.md", switch),
        _write(OUTPUT_DIR / "PREPUBLIC_REVIEW_CHECKLIST.md", checklist),
    ]
    return [str(path.relative_to(_repo_root())) for path in paths]


def _minimum_checks() -> tuple[bool, list[str], dict[str, Any]]:
    errors: list[str] = []
    no_secrets = run_no_secrets_audit()
    save_no_secrets_audit(no_secrets)
    launch_claim = run_launch_claim_guard()
    save_launch_claim_guard(launch_claim)
    message_guard = run_public_beta_message_guard(write_result=True)
    no_contact_gate = run_no_contact_launch_gate(write_result=True)
    smoke = run_smoke_all()

    if int(no_secrets.get("finding_count", 1) or 0) > 0:
        errors.append("no_secrets_audit found blocking findings.")
    if launch_claim.get("overall_token") != "PASS":
        errors.append("launch_claim_guard did not pass.")
    if message_guard.get("overall_token") != "PASS":
        errors.append("public_beta_message_guard did not pass.")
    if no_contact_gate.get("overall_token") != "PASS":
        errors.append("no_contact_launch_gate did not pass.")
    if smoke.get("pass") is not True:
        errors.append("smoke_all did not pass.")

    return not errors, errors, {
        "no_secrets": no_secrets.get("overall_token"),
        "launch_claim_guard": launch_claim.get("overall_token"),
        "public_beta_message_guard": message_guard.get("overall_token"),
        "no_contact_launch_gate": no_contact_gate.get("overall_token"),
        "smoke_all": smoke.get("pass"),
    }


def _hf_upload_changed(status_short: str) -> bool:
    return any("hf_upload/" in line.replace("\\", "/") for line in status_short.splitlines())


def run_prepublic_sync(
    execute: bool = False,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    stage_paths: list[str] | None = None,
    write_result: bool = True,
    allow_hf_reupload: bool = False,
) -> dict[str, Any]:
    written_assets = write_prepublic_assets()
    safe_paths = _safe_existing_paths(stage_paths)
    errors: list[str] = []
    warnings: list[str] = []
    status = _git(["status", "--short"], runner=runner)
    branch = _git(["branch", "--show-current"], runner=runner)
    remote = _git(["remote", "get-url", "origin"], runner=runner)
    status_short = status.get("stdout", "")
    hf_changed = _hf_upload_changed(status_short)

    result: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "would_stage": safe_paths,
        "status_short": status_short,
        "committed": False,
        "pushed": False,
        "commit_hash": None,
        "branch": (branch.get("stdout") or "main").strip() or "main",
        "remote_url": remote.get("stdout", ""),
        "hf_reupload_needed": hf_changed,
        "hf_reupload_performed": False,
        "github_visibility_changed": False,
        "hf_visibility_changed": False,
        "community_post_performed": False,
        "token_printed": False,
        "force_push_used": False,
        "warnings": warnings,
        "errors": errors,
        "checks": {},
        "written_assets": written_assets,
        "actual_publish_performed": False,
        "read_only": True,
        "live_network_used": False,
    }

    if not execute:
        result["next_action"] = "Dry run complete. Review would_stage, then run --execute for private GitHub sync only."
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    checks_ok, check_errors, check_summary = _minimum_checks()
    result["checks"] = check_summary
    if not checks_ok:
        result["errors"].extend(check_errors)
        result["next_action"] = "Resolve local audit errors before private sync."
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

    if hf_changed and allow_hf_reupload and not result["errors"]:
        warnings.append("HF upload changes detected. Re-run hf_upload_packager/audit/private upload separately if private HF sync is desired.")
    elif hf_changed:
        warnings.append("HF upload changes detected, but automatic HF re-upload was not performed by default.")

    dry_run = run_final_public_dry_run(write_result=True)
    result["final_public_dry_run_token"] = dry_run.get("overall_token")
    result["next_action"] = (
        "Private GitHub sync pushed. Review final public dry-run before any separate public switch."
        if result["pushed"] and not result["errors"]
        else "Review PREPUBLIC_SYNC_RESULT errors/warnings."
    )
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Pre-public private sync and final dry-run.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_prepublic_sync(execute=bool(args.execute) and not bool(args.dry_run))
    print(
        "prepublic_sync: "
        f"dry_run={result['dry_run']} "
        f"committed={result['committed']} "
        f"pushed={result['pushed']} "
        f"hf_reupload_performed={result['hf_reupload_performed']} "
        f"errors={len(result['errors'])}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
