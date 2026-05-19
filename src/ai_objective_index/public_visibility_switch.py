from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .hf_auth_check import check_hf_auth
from .public_launch_gate import OUTPUT_DIR, run_public_launch_gate


DRY_RUN_PATH = OUTPUT_DIR / "PUBLIC_VISIBILITY_SWITCH_DRY_RUN.json"
RESULT_PATH = OUTPUT_DIR / "PUBLIC_VISIBILITY_SWITCH_RESULT.json"
CONFIRM_ENV = "AOI_PUBLIC_LAUNCH_CONFIRM"
CONFIRM_VALUE = "YES"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _run(command: list[str], timeout: int = 90) -> dict[str, Any]:
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
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": (completed.stdout or "").strip()[:1000],
            "stderr": (completed.stderr or "").strip()[:1000],
            "command": command,
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)[:1000], "command": command}


def _gh_available() -> bool:
    return bool(shutil.which("gh"))


def _api() -> Any:
    from huggingface_hub import HfApi

    return HfApi()


def _base_result(execute: bool) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "planned_changes": [
            "GitHub repo private -> public",
            "Hugging Face Space private -> public",
            "Hugging Face Dataset private -> public",
        ],
        "github_visibility_changed": False,
        "hf_space_visibility_changed": False,
        "hf_dataset_visibility_changed": False,
        "public_switch_performed": False,
        "token_printed": False,
        "errors": [],
        "warnings": [],
        "read_only": True,
        "community_post_performed": False,
        "mcp_registry_submission_performed": False,
    }


def run_public_visibility_switch(
    execute: bool = False,
    api: Any | None = None,
    command_runner=_run,
    env: dict[str, str] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env = env if env is not None else os.environ
    result = _base_result(execute)
    result["gh_cli_available"] = _gh_available()
    result["hf_auth_available"] = False

    try:
        auth = check_hf_auth(api=api, write_result=False)
        result["hf_auth_available"] = bool(auth.get("authenticated"))
    except Exception as exc:
        result["warnings"].append(f"HF auth check not available: {str(exc)[:160]}")

    if not execute:
        result["next_action"] = f"Dry run only. To switch public, rerun with --execute and {CONFIRM_ENV}={CONFIRM_VALUE}."
        if write_result:
            _write_json(DRY_RUN_PATH, result)
            not_executed = {**result, "result_status": "not_executed_dry_run_only"}
            _write_json(RESULT_PATH, not_executed)
        return result

    if env.get(CONFIRM_ENV) != CONFIRM_VALUE:
        result["errors"].append(f"Missing explicit confirmation: set {CONFIRM_ENV}={CONFIRM_VALUE}.")
        result["next_action"] = "No visibility changes made. Set confirmation only after human review."
        if write_result:
            _write_json(RESULT_PATH, result)
        return result

    gate = run_public_launch_gate(write_result=True)
    result["gate_token"] = gate.get("overall_token")
    if gate.get("overall_token") != "PASS":
        result["errors"].append("public_launch_gate is not PASS.")
        result["next_action"] = "Resolve launch gate before visibility switch."
        if write_result:
            _write_json(RESULT_PATH, result)
        return result

    gh = command_runner(
        [
            "gh",
            "repo",
            "edit",
            "Isometric-Architect/ai-objective-index",
            "--visibility",
            "public",
            "--accept-visibility-change-consequences",
        ],
        120,
    )
    if gh.get("ok"):
        result["github_visibility_changed"] = True
    else:
        result["errors"].append(f"GitHub visibility change failed or unavailable: {gh.get('stderr')}")

    try:
        api = api or _api()
        api.update_repo_visibility(repo_id="edict-lab/ai-objective-index-demo", repo_type="space", private=False)
        result["hf_space_visibility_changed"] = True
        api.update_repo_visibility(repo_id="edict-lab/ai-objective-index-sample", repo_type="dataset", private=False)
        result["hf_dataset_visibility_changed"] = True
    except Exception as exc:
        result["errors"].append(f"Hugging Face visibility change failed or unavailable: {str(exc)[:300]}")

    result["public_switch_performed"] = (
        result["github_visibility_changed"]
        and result["hf_space_visibility_changed"]
        and result["hf_dataset_visibility_changed"]
    )
    result["next_action"] = (
        "Public visibility switch completed. Review all public pages manually."
        if result["public_switch_performed"]
        else "One or more visibility changes failed; review errors and current visibility manually."
    )
    if write_result:
        _write_json(RESULT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AOI public visibility switch gate.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_public_visibility_switch(execute=bool(args.execute) and not bool(args.dry_run))
    print(
        "public_visibility_switch: "
        f"dry_run={result['dry_run']} "
        f"public_switch_performed={result['public_switch_performed']} "
        f"errors={len(result['errors'])}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
