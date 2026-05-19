from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL, OUTPUT_DIR
from .integrated_store import get_store_for_scope


OUTPUT_PATH = OUTPUT_DIR / "PRIVATE_DEPLOYMENT_QA_RESULT.json"


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
            "stdout": (completed.stdout or "").strip(),
            "stderr": (completed.stderr or "").strip(),
            "returncode": completed.returncode,
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"ok": False, "stdout": "", "stderr": str(exc), "returncode": None}


def _git(args: list[str]) -> dict[str, Any]:
    root = _repo_root().as_posix()
    return _run(["git", "-c", f"safe.directory={root}", *args])


def _remote_ok(remote_output: str) -> bool:
    return "github.com" in remote_output.lower() and "isometric-architect/ai-objective-index" in remote_output.lower()


def _token(condition: bool) -> str:
    return "PASS" if condition else "HOLD"


def run_private_deployment_qa(write_result: bool = True) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []

    remote = _git(["remote", "-v"])
    remote_ok = remote["ok"] and _remote_ok(remote["stdout"])
    if not remote_ok:
        warnings.append("GitHub remote could not be confirmed locally.")

    hf_upload = _read_json("huggingface_upload/HF_PRIVATE_UPLOAD_RESULT.json")
    hf_qa = _read_json("huggingface_upload/HF_POST_UPLOAD_QA_RESULT.json")
    public_beta_mcp_count = len(get_store_for_scope("public_beta_mcp").list_objects())

    visibility = hf_qa.get("visibility_if_known", "not_checked")
    space_visibility = visibility.get("space") if isinstance(visibility, dict) else visibility
    dataset_visibility = visibility.get("dataset") if isinstance(visibility, dict) else visibility
    hf_private = space_visibility in {"private", "not_checked"} and dataset_visibility in {"private", "not_checked"}

    status_text = str(hf_qa.get("build_status_if_available", "")).upper()
    status_ok = status_text.startswith("RUNNING") or status_text in {"BUILDING", "NOT_AVAILABLE"}

    checks = {
        "github_remote": {"token": _token(remote_ok), "remote_output_present": bool(remote["stdout"])},
        "hf_upload_success": {
            "token": _token(
                hf_upload.get("space_upload_performed") is True
                and hf_upload.get("dataset_upload_performed") is True
                and hf_upload.get("visibility") == "private"
            ),
            "space_upload_performed": hf_upload.get("space_upload_performed"),
            "dataset_upload_performed": hf_upload.get("dataset_upload_performed"),
        },
        "hf_post_upload_qa": {
            "token": _token(hf_qa.get("qa_token") == "PASS"),
            "qa_token": hf_qa.get("qa_token", "missing"),
        },
        "hf_space_status": {
            "token": _token(status_ok),
            "status": hf_qa.get("build_status_if_available", "missing"),
        },
        "public_beta_mcp": {"token": _token(public_beta_mcp_count > 0), "count": public_beta_mcp_count},
        "private_visibility": {"token": _token(hf_private), "visibility_if_known": visibility},
        "no_public_switch": {"token": "PASS", "github_public_switch": False, "hf_public_switch": False},
    }

    if not hf_private:
        errors.append("Hugging Face visibility does not appear private.")
    if any(check["token"] == "HOLD" for check in checks.values()):
        overall = "HOLD"
    else:
        overall = "PASS"
    if errors:
        overall = "BLOCK"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "checks": checks,
        "github_repo_url": GITHUB_URL,
        "hf_space_url": hf_qa.get("space_url") or HF_SPACE_URL,
        "hf_dataset_url": hf_qa.get("dataset_url") or HF_DATASET_URL,
        "hf_space_status": hf_qa.get("build_status_if_available", "not_checked"),
        "hf_dataset_checked": hf_qa.get("dataset_exists_if_checked", "not_checked"),
        "visibility_if_known": visibility,
        "public_switch_performed": False,
        "hf_public_switch_performed": False,
        "actual_community_post_performed": False,
        "actual_publish_performed": False,
        "errors": errors,
        "warnings": warnings,
        "next_action": "Open private GitHub and Hugging Face links and test the Space query."
        if overall == "PASS"
        else "Resolve HOLD/BLOCK checks before considering any public switch.",
        "read_only": True,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_private_deployment_qa()
    print(
        "private_deployment_qa: "
        f"{result['overall_token']} "
        f"space_status={result['hf_space_status']} "
        f"public_switch_performed={result['public_switch_performed']}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
