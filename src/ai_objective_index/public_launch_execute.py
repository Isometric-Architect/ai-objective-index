from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .final_public_dry_run import run_final_public_dry_run
from .hf_auth_check import check_hf_auth
from .launch_claim_guard import run_launch_claim_guard
from .no_contact_launch_gate import run_no_contact_launch_gate
from .no_secrets_audit import run_no_secrets_audit
from .public_beta_message_guard import run_public_beta_message_guard
from .public_launch_gate import OUTPUT_DIR
from .smoke_all import run_smoke_all


OUTPUT_PATH = OUTPUT_DIR / "PUBLIC_LAUNCH_EXECUTE_RESULT.json"
CONFIRM_ENV = "AOI_PUBLIC_LAUNCH_CONFIRM"
CONFIRM_VALUE = "YES"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _sanitize(value: Any) -> str:
    text = str(value or "")
    for marker in ["gho_", "ghp_", "hf_", "bearer ", "api_key=", "password="]:
        index = text.lower().find(marker)
        if index >= 0:
            text = text[:index] + "[redacted]"
            break
    return text[:1000]


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
            "command": command[:4],
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command[:4], "ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def _api() -> Any:
    from huggingface_hub import HfApi

    return HfApi()


def _base_result(execute: bool, env_confirm_present: bool) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "env_confirm_present": env_confirm_present,
        "github_visibility_changed": False,
        "hf_space_visibility_changed": False,
        "hf_dataset_visibility_changed": False,
        "public_switch_performed": False,
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "token_printed": False,
        "errors": [],
        "warnings": [],
        "checks": {},
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "force_push_used": False,
        "read_only": True,
    }


def _required_checks() -> tuple[bool, list[str], dict[str, Any]]:
    errors: list[str] = []
    final_dry_run = run_final_public_dry_run(write_result=True)
    no_contact = run_no_contact_launch_gate(write_result=True)
    message_guard = run_public_beta_message_guard(write_result=True)
    no_secrets = run_no_secrets_audit()
    launch_claim = run_launch_claim_guard()
    smoke = run_smoke_all()

    no_secret_findings = int(no_secrets.get("finding_count", 0) or 0)
    if final_dry_run.get("overall_token") != "PASS":
        errors.append("final_public_dry_run is not PASS.")
    if no_contact.get("overall_token") != "PASS":
        errors.append("no_contact_launch_gate is not PASS.")
    if message_guard.get("overall_token") != "PASS":
        errors.append("public_beta_message_guard is not PASS.")
    if no_secret_findings > 0:
        errors.append("no_secrets_audit found blocking token/secret findings.")
    if launch_claim.get("overall_token") != "PASS":
        errors.append("launch_claim_guard is not PASS.")
    if smoke.get("pass") is not True:
        errors.append("smoke_all did not pass.")

    return not errors, errors, {
        "final_public_dry_run": final_dry_run.get("overall_token"),
        "no_contact_launch_gate": no_contact.get("overall_token"),
        "public_beta_message_guard": message_guard.get("overall_token"),
        "no_secrets_audit": no_secrets.get("overall_token"),
        "no_secret_findings": no_secret_findings,
        "launch_claim_guard": launch_claim.get("overall_token"),
        "smoke_all": smoke.get("pass"),
    }


def _switch_github(command_runner: Callable[[list[str], int], dict[str, Any]]) -> tuple[bool, str | None]:
    if not shutil.which("gh"):
        return False, "GitHub CLI is not available. Change repository visibility manually in GitHub settings."
    command = [
        "gh",
        "repo",
        "edit",
        "Isometric-Architect/ai-objective-index",
        "--visibility",
        "public",
        "--accept-visibility-change-consequences",
    ]
    result = command_runner(command, 180)
    if result.get("ok"):
        return True, None
    return False, f"GitHub visibility change failed or was not confirmed: {_sanitize(result.get('stderr') or result.get('stdout'))}"


def _switch_huggingface(api: Any | None) -> tuple[bool, bool, list[str]]:
    errors: list[str] = []
    api = api or _api()

    def set_public(repo_id: str, repo_type: str) -> None:
        if hasattr(api, "update_repo_visibility"):
            api.update_repo_visibility(repo_id=repo_id, repo_type=repo_type, private=False)
            return
        api.update_repo_settings(repo_id=repo_id, repo_type=repo_type, private=False)

    try:
        set_public("edict-lab/ai-objective-index-demo", "space")
        space_ok = True
    except Exception as exc:
        space_ok = False
        errors.append(f"Hugging Face Space visibility change failed: {_sanitize(exc)}")
    try:
        set_public("edict-lab/ai-objective-index-sample", "dataset")
        dataset_ok = True
    except Exception as exc:
        dataset_ok = False
        errors.append(f"Hugging Face Dataset visibility change failed: {_sanitize(exc)}")
    return space_ok, dataset_ok, errors


def write_post_public_assets() -> list[str]:
    checklist = """# Post-Public Review Checklist

- [ ] Open GitHub URL in incognito/private browser.
- [ ] Confirm README renders.
- [ ] Open Hugging Face Space URL.
- [ ] Run sample query: `browser automation MCP server`.
- [ ] Open Hugging Face Dataset URL.
- [ ] Confirm dataset card says not verified and not security certified.
- [ ] Confirm issue templates are visible.
- [ ] Confirm no token or secret appears.
- [ ] Do not post community message yet unless separately decided.
"""
    hold = """# Community Post HOLD Note

Public visibility switch is not the same as community launch.

Wait until URLs are checked. Community posting should be Package 8L or a separate explicit user decision. Use only the conservative no-contact draft, and do not claim verified, safe, security certified, quality guaranteed, production-ready, or purchasing advice.
"""
    token = """# Token Revoke After Public Note

If no further Hugging Face upload is needed, revoke the temporary token locally:

Hugging Face Settings -> Access Tokens -> aoi-private-upload -> Delete/Revoke.

Do not paste tokens into chat. Do not commit tokens. If further Hugging Face updates are needed, keep the token local only.
"""
    paths = [
        _write(OUTPUT_DIR / "POST_PUBLIC_REVIEW_CHECKLIST.md", checklist),
        _write(OUTPUT_DIR / "COMMUNITY_POST_HOLD_NOTE.md", hold),
        _write(OUTPUT_DIR / "TOKEN_REVOKE_AFTER_PUBLIC_NOTE.md", token),
    ]
    return [str(path.relative_to(_repo_root())) for path in paths]


def run_public_launch_execute(
    execute: bool = False,
    env: dict[str, str] | None = None,
    api: Any | None = None,
    command_runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    env = env if env is not None else os.environ
    env_confirm_present = env.get(CONFIRM_ENV) == CONFIRM_VALUE
    result = _base_result(execute=execute, env_confirm_present=env_confirm_present)
    result["written_assets"] = write_post_public_assets()

    if not execute:
        checks_ok, check_errors, check_summary = _required_checks()
        result["checks"] = check_summary
        result["warnings"].extend(check_errors)
        result["next_action"] = f"Dry run only. To execute later, set {CONFIRM_ENV}={CONFIRM_VALUE} and rerun with --execute."
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    if not env_confirm_present:
        result["errors"].append(f"Missing explicit confirmation: set {CONFIRM_ENV}={CONFIRM_VALUE}.")
        result["next_action"] = "No visibility changes made. Set confirmation only after human review."
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    checks_ok, check_errors, check_summary = _required_checks()
    result["checks"] = check_summary
    if not checks_ok:
        result["errors"].extend(check_errors)
        result["next_action"] = "No visibility changes made. Resolve HOLD/BLOCK checks first."
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    hf_auth = check_hf_auth(api=api, write_result=True)
    result["huggingface_authenticated"] = bool(hf_auth.get("authenticated"))

    github_ok, github_error = _switch_github(command_runner)
    result["github_visibility_changed"] = github_ok
    if github_error:
        result["errors"].append(github_error)

    if result["huggingface_authenticated"]:
        space_ok, dataset_ok, hf_errors = _switch_huggingface(api)
        result["hf_space_visibility_changed"] = space_ok
        result["hf_dataset_visibility_changed"] = dataset_ok
        result["errors"].extend(hf_errors)
    else:
        result["errors"].append("Hugging Face authentication unavailable. Change Space/Dataset visibility manually.")

    result["public_switch_performed"] = (
        result["github_visibility_changed"]
        and result["hf_space_visibility_changed"]
        and result["hf_dataset_visibility_changed"]
    )
    result["next_action"] = (
        "Public visibility switch completed. Run public_url_qa and post_public_state_report."
        if result["public_switch_performed"]
        else "One or more visibility changes failed or need manual completion. Review errors."
    )
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Execute AOI public visibility switch after explicit confirmation.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_public_launch_execute(execute=bool(args.execute) and not bool(args.dry_run))
    print(
        "public_launch_execute: "
        f"dry_run={result['dry_run']} "
        f"public_switch_performed={result['public_switch_performed']} "
        f"github={result['github_visibility_changed']} "
        f"hf_space={result['hf_space_visibility_changed']} "
        f"hf_dataset={result['hf_dataset_visibility_changed']} "
        f"errors={len(result['errors'])}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
