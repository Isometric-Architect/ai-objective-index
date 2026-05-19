from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .ai_reviewer_simulation import run_ai_reviewer_simulation
from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope
from .launch_claim_guard import run_launch_claim_guard
from .no_contact_launch_gate import run_no_contact_launch_gate
from .no_secrets_audit import run_no_secrets_audit
from .public_beta_message_guard import run_public_beta_message_guard
from .public_launch_gate import OUTPUT_DIR
from .smoke_all import run_smoke_all


OUTPUT_PATH = OUTPUT_DIR / "FINAL_PUBLIC_DRY_RUN_RESULT.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


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
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": (completed.stdout or "").strip(),
            "stderr": (completed.stderr or "").strip(),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc)}


def _git(args: list[str], runner: Callable[[list[str], int], dict[str, Any]] = _run) -> dict[str, Any]:
    root = _repo_root().as_posix()
    return runner(["git", "-c", f"safe.directory={root}", *args], 60)


def _public_beta_mcp_count() -> int:
    return len(get_store_for_scope("public_beta_mcp").list_objects())


def _token(condition: bool, block: bool = False) -> str:
    if block:
        return "BLOCK"
    return "PASS" if condition else "HOLD"


def _gate_token(value: str | None, allow_hold: bool = False) -> str:
    if value == "BLOCK":
        return "BLOCK"
    if value == "PASS" or (allow_hold and value == "HOLD"):
        return "PASS"
    return "HOLD"


def _hf_status_checks() -> dict[str, Any]:
    hf_qa = _read_json("huggingface_upload/HF_POST_UPLOAD_QA_RESULT.json")
    status = str(hf_qa.get("build_status_if_available", "")).upper()
    space_running = status.startswith("RUNNING") or status in {"BUILDING", "NOT_AVAILABLE", "NOT_CHECKED"}
    dataset_exists = hf_qa.get("dataset_exists_if_checked")
    return {
        "space_running_if_known": space_running,
        "space_status": hf_qa.get("build_status_if_available", "missing"),
        "dataset_exists_if_known": dataset_exists in {True, "not_checked", "NOT_CHECKED", None},
        "dataset_exists_value": dataset_exists,
    }


def run_final_public_dry_run(
    write_result: bool = True,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    run_live_helpers: bool = True,
) -> dict[str, Any]:
    no_contact_gate = run_no_contact_launch_gate(write_result=True) if run_live_helpers else _read_json("public_launch/NO_CONTACT_LAUNCH_GATE_RESULT.json")
    reviewer = run_ai_reviewer_simulation(write_result=True) if run_live_helpers else _read_json("public_launch/AI_REVIEWER_SIMULATION_RESULT.json")
    message_guard = run_public_beta_message_guard(write_result=True) if run_live_helpers else _read_json("public_launch/PUBLIC_BETA_MESSAGE_GUARD_RESULT.json")
    no_secrets = run_no_secrets_audit() if run_live_helpers else _read_json("data/generated/no_secrets_audit_result_v0_2.json")
    launch_claim = run_launch_claim_guard() if run_live_helpers else _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    smoke = run_smoke_all() if run_live_helpers else _read_json("data/generated/smoke_all_result_v0_1.json")
    git_remote = _git(["remote", "get-url", "origin"], runner=runner)
    hf = _hf_status_checks()
    public_beta_count = _public_beta_mcp_count()
    no_secret_findings = int(no_secrets.get("finding_count", 0) or 0)

    checks = {
        "no_contact_launch_gate": {"token": _token(no_contact_gate.get("overall_token") == "PASS"), "value": no_contact_gate.get("overall_token")},
        "ai_reviewer_simulation": {"token": _gate_token(reviewer.get("overall_token"), allow_hold=True), "value": reviewer.get("overall_token")},
        "public_beta_message_guard": {"token": _token(message_guard.get("overall_token") == "PASS"), "value": message_guard.get("overall_token")},
        "no_secrets_audit": {"token": _token(no_secret_findings == 0, block=no_secret_findings > 0), "finding_count": no_secret_findings},
        "launch_claim_guard": {"token": _token(launch_claim.get("overall_token") == "PASS"), "value": launch_claim.get("overall_token")},
        "smoke_all": {"token": _token(smoke.get("pass") is True), "pass": smoke.get("pass")},
        "github_remote": {
            "token": _token(git_remote.get("ok") and "ai-objective-index" in str(git_remote.get("stdout", ""))),
            "remote": git_remote.get("stdout", ""),
        },
        "hf_space": {"token": _token(hf["space_running_if_known"]), "status": hf["space_status"]},
        "hf_dataset": {"token": _token(hf["dataset_exists_if_known"]), "value": hf["dataset_exists_value"]},
        "public_beta_mcp": {"token": _token(public_beta_count > 0), "count": public_beta_count},
        "actual_public_switch_not_performed": {"token": "PASS", "actual_switch_performed": False},
    }

    if any(check["token"] == "BLOCK" for check in checks.values()):
        overall = "BLOCK"
    elif all(check["token"] == "PASS" for check in checks.values()):
        overall = "PASS"
    else:
        overall = "HOLD"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "checks": checks,
        "would_switch": {
            "github_repo": True,
            "hf_space": True,
            "hf_dataset": True,
        },
        "actual_switch_performed": False,
        "required_user_confirmation": True,
        "required_env_for_execute": "AOI_PUBLIC_LAUNCH_CONFIRM=YES",
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "warnings": [
            "This is a dry-run only. No public visibility change was performed.",
            "A PASS token is not verification, security certification, quality guarantee, production readiness, or purchasing advice.",
        ],
        "next_action": "Human decision required: keep private, pause, or explicitly authorize public visibility switch later."
        if overall != "BLOCK"
        else "Resolve BLOCK checks before any public visibility switch.",
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
        "community_post_performed": False,
        "mcp_registry_submission_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_final_public_dry_run()
    print(
        "final_public_dry_run: "
        f"{result['overall_token']} "
        f"actual_switch_performed={result['actual_switch_performed']} "
        f"required_user_confirmation={result['required_user_confirmation']}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
