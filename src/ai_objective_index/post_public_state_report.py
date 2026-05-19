from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope
from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "POST_PUBLIC_STATE_REPORT.json"


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


def run_post_public_state_report(write_result: bool = True) -> dict[str, Any]:
    execute = _read_json("public_launch/PUBLIC_LAUNCH_EXECUTE_RESULT.json")
    url_qa = _read_json("public_launch/PUBLIC_URL_QA_RESULT.json")
    visibility_status = {
        "github": "public" if execute.get("github_visibility_changed") else "not_changed_or_not_checked",
        "hf_space": "public" if execute.get("hf_space_visibility_changed") else "not_changed_or_not_checked",
        "hf_dataset": "public" if execute.get("hf_dataset_visibility_changed") else "not_changed_or_not_checked",
        "url_qa_token": url_qa.get("overall_token", "not_checked"),
    }
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "public_beta_mcp_count": len(get_store_for_scope("public_beta_mcp").list_objects()),
        "visibility_status": visibility_status,
        "community_post_performed": False,
        "mcp_registry_submission_performed": False,
        "github_release_created": False,
        "token_revocation_recommended": True,
        "next_options": {
            "A": "wait and observe",
            "B": "create GitHub Release",
            "C": "post conservative community feedback request",
            "D": "submit MCP Registry later",
        },
        "warnings": [
            "Public visibility is not a community launch.",
            "Do not claim verification, security certification, quality guarantee, production readiness, or purchasing advice.",
        ],
        "read_only": True,
        "actual_publish_performed": bool(execute.get("public_switch_performed")),
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_post_public_state_report()
    print(
        "post_public_state_report: "
        f"public_beta_mcp={result['public_beta_mcp_count']} "
        f"github={result['visibility_status']['github']} "
        f"hf_space={result['visibility_status']['hf_space']} "
        f"hf_dataset={result['visibility_status']['hf_dataset']}"
    )
    print("next_options=A wait | B GitHub Release | C community feedback | D MCP Registry later")


if __name__ == "__main__":
    main()
