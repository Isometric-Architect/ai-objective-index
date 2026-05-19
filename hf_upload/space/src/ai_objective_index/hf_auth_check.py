from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


OUTPUT_DIR = Path("huggingface_upload")
OUTPUT_PATH = OUTPUT_DIR / "HF_AUTH_STATUS.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _sanitize(value: Any) -> str:
    text = str(value or "")
    for prefix in ["hf_", "api_key=", "password=", "bearer "]:
        index = text.lower().find(prefix)
        if index >= 0:
            text = text[:index] + "[redacted]"
            break
    return text[:500]


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
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def _package_available() -> bool:
    try:
        import huggingface_hub  # noqa: F401
    except Exception:
        return False
    return True


def _cli_candidates() -> list[list[str]]:
    candidates: list[list[str]] = []
    if shutil.which("hf"):
        candidates.append(["hf", "auth", "whoami"])
    if shutil.which("huggingface-cli"):
        candidates.append(["huggingface-cli", "whoami"])
    return candidates


def _extract_username_from_cli(output: str) -> str | None:
    text = (output or "").strip()
    if not text:
        return None
    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned or "token" in cleaned.lower():
            continue
        if "logged in as" in cleaned.lower():
            return cleaned.split()[-1].strip(".")
        if cleaned.startswith("name:"):
            return cleaned.split(":", 1)[1].strip()
        if "@" not in cleaned and " " not in cleaned:
            return cleaned
    return None


def check_hf_auth(
    api: Any | None = None,
    command_runner: Callable[[list[str]], dict[str, Any]] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    package_available = _package_available()
    cli_commands = _cli_candidates()
    cli_available = bool(cli_commands)
    command_runner = command_runner or _run
    authenticated = False
    username: str | None = None
    checks: list[dict[str, Any]] = []

    for command in cli_commands:
        result = command_runner(command)
        checks.append(
            {
                "method": "cli",
                "command": command[:2],
                "ok": bool(result.get("ok")),
                "stdout_preview": _sanitize(result.get("stdout")),
                "stderr_preview": _sanitize(result.get("stderr")),
            }
        )
        if result.get("ok"):
            authenticated = True
            username = _extract_username_from_cli(str(result.get("stdout") or result.get("stderr") or ""))
            break

    if not authenticated and package_available:
        try:
            if api is None:
                from huggingface_hub import HfApi

                api = HfApi()
            whoami = api.whoami()
            authenticated = True
            if isinstance(whoami, dict):
                username = whoami.get("name") or whoami.get("fullname") or whoami.get("user")
            else:
                username = str(whoami)
            checks.append({"method": "HfApi.whoami", "ok": True})
        except Exception as exc:
            checks.append({"method": "HfApi.whoami", "ok": False, "error": _sanitize(exc)})

    next_action = (
        "Hugging Face CLI/API authentication is available."
        if authenticated
        else "Run hf auth login or huggingface-cli login locally. Do not paste tokens into chat or commit tokens."
    )
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "hf_package_available": package_available,
        "hf_cli_available": cli_available,
        "authenticated": authenticated,
        "username_if_known": username,
        "token_printed": False,
        "checks": checks,
        "recommended_next_action": next_action,
        "read_only": True,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = check_hf_auth()
    print(
        "hf_auth_check: "
        f"package={result['hf_package_available']} "
        f"cli={result['hf_cli_available']} "
        f"authenticated={result['authenticated']} "
        f"username={result.get('username_if_known') or 'unknown'} "
        "token_printed=False"
    )
    print(f"next_action={result['recommended_next_action']}")


if __name__ == "__main__":
    main()
