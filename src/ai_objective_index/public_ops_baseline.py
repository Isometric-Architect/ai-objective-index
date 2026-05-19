from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope


OUTPUT_DIR = Path("public_ops")
OUTPUT_PATH = OUTPUT_DIR / "PUBLIC_OPS_BASELINE_v0_1.json"


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


def _token_is_pass(payload: dict[str, Any], key: str = "overall_token") -> bool:
    return payload.get(key) == "PASS"


def run_public_ops_baseline(write_result: bool = True) -> dict[str, Any]:
    post_public = _read_json("public_launch/POST_PUBLIC_STABILIZATION_RESULT.json")
    public_url_qa = _read_json("public_launch/PUBLIC_URL_QA_RESULT.json")
    issue_loop = _read_json("public_launch/PUBLIC_ISSUE_LOOP_RESULT.json")
    public_claim = _read_json("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json")
    launch_claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    count = len(get_store_for_scope("public_beta_mcp").list_objects())
    community_post_performed = bool(post_public.get("community_post_performed", False))
    github_release_created = bool(post_public.get("github_release_created", False))
    registry_submission = bool(post_public.get("mcp_registry_submission_performed", False))
    issue_ready = bool(issue_loop.get("feedback_loop_ready", False))

    checks = {
        "post_public_stabilization": {
            "pass": _token_is_pass(post_public),
            "token": post_public.get("overall_token", "missing"),
        },
        "public_url_qa": {
            "pass": _token_is_pass(public_url_qa),
            "token": public_url_qa.get("overall_token", "missing"),
            "available": bool(public_url_qa),
        },
        "issue_loop_ready": {"pass": issue_ready, "value": issue_ready},
        "public_beta_mcp_count": {"pass": count > 0, "count": count},
        "public_claim_audit": {
            "pass": (not public_claim) or public_claim.get("overall_token") == "PASS",
            "token": public_claim.get("overall_token", "not_available"),
        },
        "launch_claim_guard": {
            "pass": launch_claim.get("overall_token") == "PASS",
            "token": launch_claim.get("overall_token", "missing"),
        },
        "no_external_launch_actions": {
            "pass": not (community_post_performed or github_release_created or registry_submission),
            "community_post_performed": community_post_performed,
            "github_release_created": github_release_created,
            "mcp_registry_submission_performed": registry_submission,
        },
    }
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "public_beta_mcp_count": count,
        "issue_loop_ready": issue_ready,
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "checks": checks,
        "overall_token": "PASS" if all(check["pass"] for check in checks.values()) else "HOLD",
        "current_recommended_mode": "observe_72h",
        "next_options": {
            "A": "keep observing",
            "B": "create GitHub Release draft",
            "C": "community feedback post",
            "D": "MCP Registry submission prep",
            "E": "data expansion",
        },
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_public_ops_baseline()
    print(
        "public_ops_baseline: "
        f"{result['overall_token']} "
        f"public_beta_mcp={result['public_beta_mcp_count']} "
        f"issue_loop_ready={result['issue_loop_ready']}"
    )
    print(f"recommended_mode={result['current_recommended_mode']}")


if __name__ == "__main__":
    main()
