from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope
from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "PREPUBLIC_STATE_REPORT.json"


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


def _public_beta_mcp_count() -> int:
    return len(get_store_for_scope("public_beta_mcp").list_objects())


def run_prepublic_state_report(write_result: bool = True) -> dict[str, Any]:
    no_contact = _read_json("public_launch/NO_CONTACT_LAUNCH_GATE_RESULT.json")
    message_guard = _read_json("public_launch/PUBLIC_BETA_MESSAGE_GUARD_RESULT.json")
    dry_run = _read_json("public_launch/FINAL_PUBLIC_DRY_RUN_RESULT.json")
    pytest_count = None
    if (_repo_root() / "tests").exists():
        pytest_count = len(list((_repo_root() / "tests").glob("test_*.py")))

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "github_repo_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "tests_file_count": pytest_count,
        "last_known_pytest_result": "239 passed or newer, see latest terminal/test run",
        "public_beta_mcp_count": _public_beta_mcp_count(),
        "no_contact_gate_token": no_contact.get("overall_token", "not_checked"),
        "message_guard_token": message_guard.get("overall_token", "not_checked"),
        "final_public_dry_run_token": dry_run.get("overall_token", "not_checked"),
        "public_visibility_status_if_known": "private_or_not_checked",
        "token_revocation_reminder": "If no more Hugging Face upload is needed, revoke temporary upload tokens locally. Do not paste tokens into chat or commit them.",
        "next_options": {
            "A": "keep private",
            "B": "public switch after explicit confirmation",
            "C": "pause and improve docs",
        },
        "public_switch_performed": False,
        "community_post_performed": False,
        "mcp_registry_submission_performed": False,
        "read_only": True,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_prepublic_state_report()
    print(
        "prepublic_state_report: "
        f"public_beta_mcp={result['public_beta_mcp_count']} "
        f"no_contact_gate={result['no_contact_gate_token']} "
        f"message_guard={result['message_guard_token']}"
    )
    print("next_options=A keep private | B public switch | C pause")


if __name__ == "__main__":
    main()
