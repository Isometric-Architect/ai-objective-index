from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .hf_auth_check import check_hf_auth
from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "TOKEN_REVOCATION_VERIFY_RESULT.json"

MANUAL_STEPS = [
    "Open Hugging Face Settings.",
    "Open Access Tokens.",
    "Delete/Revoke aoi-private-upload.",
    "Do not paste token into chat.",
    "If later update is needed, create a new temporary token.",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def run_token_revocation_verify(
    auth_checker: Callable[..., dict[str, Any]] = check_hf_auth,
    write_result: bool = True,
) -> dict[str, Any]:
    try:
        auth = auth_checker(write_result=False)
    except TypeError:
        auth = auth_checker()
    except Exception as exc:
        auth = {"authenticated": False, "error": str(exc)[:300], "token_printed": False}

    huggingface_auth_available = bool(auth.get("authenticated"))
    verification_note = (
        "Temporary upload token may still be active or another HF credential is available."
        if huggingface_auth_available
        else "HF token/auth no longer active in this environment."
    )
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "hf_auth_available": huggingface_auth_available,
        "token_printed": False,
        "token_committed": False,
        "revoke_recommended": True,
        "manual_steps": MANUAL_STEPS,
        "verification_note": verification_note,
        "next_action": "Revoke the temporary Hugging Face token if no further upload is needed.",
        "auth_check": {
            "hf_package_available": auth.get("hf_package_available"),
            "hf_cli_available": auth.get("hf_cli_available"),
            "authenticated": huggingface_auth_available,
            "username_if_known": auth.get("username_if_known"),
            "token_printed": False,
        },
        "read_only": True,
        "live_network_used": False,
        "actual_revocation_performed": False,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_token_revocation_verify()
    print(
        "token_revocation_verify: "
        f"hf_auth_available={result['hf_auth_available']} "
        f"revoke_recommended={result['revoke_recommended']} "
        "token_printed=False"
    )
    print(f"verification_note={result['verification_note']}")


if __name__ == "__main__":
    main()
