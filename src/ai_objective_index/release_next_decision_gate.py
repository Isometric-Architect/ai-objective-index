from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .public_ops_baseline import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "RELEASE_NEXT_DECISION_GATE.json"


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


def run_release_next_decision_gate(write_result: bool = True) -> dict[str, Any]:
    baseline = _read_json("public_ops/PUBLIC_OPS_BASELINE_v0_1.json")
    hygiene = _read_json("public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json")
    public_url = _read_json("public_launch/PUBLIC_URL_QA_RESULT.json")
    public_claim = _read_json("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json")
    launch_claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    issue_loop = _read_json("public_launch/PUBLIC_ISSUE_LOOP_RESULT.json")

    reasons: list[str] = []
    if public_url and public_url.get("overall_token") not in {"PASS", "NOT_CHECKED"}:
        recommendation = "fix_public_deployment"
        reasons.append("public_url_qa is not PASS/NOT_CHECKED.")
    elif hygiene.get("overall_token") == "BLOCK":
        recommendation = "clean_repo"
        reasons.append("worktree hygiene has do_not_commit entries.")
    elif public_claim.get("overall_token") not in {None, "PASS"} or launch_claim.get("overall_token") not in {None, "PASS"}:
        recommendation = "fix_wording"
        reasons.append("claim audit did not pass.")
    elif baseline and baseline.get("overall_token") not in {"PASS", "HOLD"}:
        recommendation = "fix_public_ops_baseline"
        reasons.append("public ops baseline has blocking issues.")
    else:
        recommendation = "observe_72h"
        reasons.append("Default recommendation: observe public links and issue loop before next launch action.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "recommendation": recommendation,
        "next_package_options": {
            "A": "keep observing",
            "B": "create GitHub Release draft",
            "C": "community feedback post",
            "D": "MCP Registry submission prep",
            "E": "data expansion",
        },
        "inputs": {
            "public_ops_baseline": baseline.get("overall_token", "missing"),
            "issue_loop_ready": issue_loop.get("feedback_loop_ready", False),
            "public_url_qa": public_url.get("overall_token", "missing"),
            "worktree_hygiene": hygiene.get("overall_token", "missing"),
            "public_launch_claim_audit": public_claim.get("overall_token", "missing"),
            "launch_claim_guard": launch_claim.get("overall_token", "missing"),
        },
        "reasons": reasons,
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_release_next_decision_gate()
    print(f"release_next_decision_gate: recommendation={result['recommendation']}")
    print(f"reason={result['reasons'][0] if result['reasons'] else 'none'}")


if __name__ == "__main__":
    main()
